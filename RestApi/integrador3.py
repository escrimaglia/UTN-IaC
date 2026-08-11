# Integrador: del modelo de datos a la API, con reconciliacion declarativa.
#
# Es el mismo problema del capitulo 12 (Netmiko) y del 18 (Ansible),
# resuelto por tercera vez. La diferencia: con datos estructurados se puede
# calcular el diff, asi que la idempotencia sale casi gratis.
#
# Uso:
#   python integrador3.py --dry-run     ← simula, no cambia nada  (--check)
#   python integrador3.py               ← aplica
#   python integrador3.py --estricto    ← ademas BORRA lo no declarado
#
# By Ed Scrimaglia

import sys
import yaml
from pathlib import Path
from dataclasses import dataclass, field

from rest_clase import RestClient, RestError
from datos_device import datos_device

MODELO = Path(__file__).parent / "modelo_datos.yaml"
HOSTNAME = "SW-Bld_A"


# ─── El plan de cambios: se calcula primero, se aplica despues ──────────
@dataclass
class Plan:
    """Principio 4 del capitulo 1: generar primero, aplicar despues.

    Aca el 'artefacto revisable' no es un .cfg: es esta estructura.
    """
    crear: list[tuple[int, str]] = field(default_factory=list)
    renombrar: list[tuple[int, str, str]] = field(default_factory=list)
    borrar: list[tuple[int, str]] = field(default_factory=list)
    interfaces: list[tuple[str, dict, dict]] = field(default_factory=list)

    def a_aplicar(self, estricto: bool) -> int:
        """Cuantos cambios se van a ejecutar realmente en este modo.

        La deriva detectada solo cuenta si se pidio --estricto: sin eso se
        reporta pero no se toca, y el resultado tiene que ser changed=0.
        """
        return (len(self.crear) + len(self.renombrar) + len(self.interfaces)
                + (len(self.borrar) if estricto else 0))

    @property
    def vacio(self) -> bool:
        return not (self.crear or self.renombrar or self.borrar or self.interfaces)

    def mostrar(self, estricto: bool) -> None:
        if self.vacio:
            print("   (sin cambios: la realidad ya coincide con el modelo)")
            return
        for vlan_id, nombre in self.crear:
            print(f"   + VLAN {vlan_id} '{nombre}'")
        for vlan_id, viejo, nuevo in self.renombrar:
            print(f"   ~ VLAN {vlan_id} '{viejo}' → '{nuevo}'")
        for vlan_id, nombre in self.borrar:
            marca = "-" if estricto else "!"
            nota = "" if estricto else "   (deriva: usar --estricto para borrarla)"
            print(f"   {marca} VLAN {vlan_id} '{nombre}' no esta en el modelo{nota}")
        for nombre, actual, deseado in self.interfaces:
            campos = ", ".join(f"{k}: {actual.get(k)!r} → {v!r}"
                               for k, v in deseado.items())
            print(f"   ~ {nombre}: {campos}")


def cargar_modelo(ruta: Path, hostname: str) -> dict:
    with open(ruta) as f:
        modelo = yaml.safe_load(f)
    devices = modelo["modelo"]["infra_spec"]["devices"]
    if hostname not in devices:
        # El error mas frecuente de la Parte IV (cap. 14 §14.8), con
        # un mensaje que dice exactamente que hay disponible.
        raise KeyError(f"'{hostname}' no esta en el modelo. "
                       f"Claves disponibles: {sorted(devices)}")
    return devices[hostname]


def calcular_plan(deseado: dict, vlans_reales: dict[int, str],
                  interfaces_reales: dict[str, dict]) -> Plan:
    """Compara deseado contra real. No toca nada: solo calcula."""
    plan = Plan()

    # ─── VLANs ────────────────────────────────────────────────────────
    vlans_deseadas = {v["id"]: v["name"] for v in deseado["vlans"]}

    for vlan_id, nombre in sorted(vlans_deseadas.items()):
        if vlan_id not in vlans_reales:
            plan.crear.append((vlan_id, nombre))
        elif vlans_reales[vlan_id] != nombre:
            plan.renombrar.append((vlan_id, vlans_reales[vlan_id], nombre))

    # Lo que existe en el equipo y NO esta en el modelo: deriva (cap. 21 §21.3)
    for vlan_id, nombre in sorted(vlans_reales.items()):
        if vlan_id not in vlans_deseadas and vlan_id != 1:
            plan.borrar.append((vlan_id, nombre))

    # ─── Interfaces ───────────────────────────────────────────────────
    for inter in deseado["interfaces"]:
        nombre = inter["name"]
        actual = interfaces_reales.get(nombre)
        if actual is None:
            print(f"   ⚠️  {nombre} esta en el modelo y no en el equipo: se omite")
            continue

        # Solo los campos que difieren. Esto es lo que hace idempotente al script.
        cambios: dict = {}
        if actual.get("description") != inter["description"]:
            cambios["description"] = inter["description"]
        if actual.get("mode") != inter["mode"]:
            cambios["mode"] = inter["mode"]
        if inter["mode"] == "access" and actual.get("vlan") != inter["vlan"]:
            cambios["vlan"] = inter["vlan"]
        if not actual.get("enabled"):
            cambios["enabled"] = True

        if cambios:
            plan.interfaces.append((nombre, actual, cambios))

    return plan


def aplicar_plan(api: RestClient, plan: Plan, estricto: bool) -> int:
    """Ejecuta el plan. Devuelve la cantidad de cambios realizados."""
    cambios = 0

    for vlan_id, nombre in plan.crear:
        api.create_vlan(vlan_id, nombre)
        print(f"   ✅ VLAN {vlan_id} '{nombre}' creada")
        cambios += 1

    for vlan_id, _viejo, nuevo in plan.renombrar:
        api.rename_vlan(vlan_id, nuevo)
        print(f"   ✅ VLAN {vlan_id} renombrada a '{nuevo}'")
        cambios += 1

    if estricto:
        for vlan_id, nombre in plan.borrar:
            api.delete_vlan(vlan_id)
            print(f"   ✅ VLAN {vlan_id} '{nombre}' eliminada (deriva)")
            cambios += 1

    # Las interfaces van DESPUES de las VLANs: un puerto de acceso no puede
    # apuntar a una VLAN que todavia no existe (cap. 18 §18.4).
    for nombre, _actual, campos in plan.interfaces:
        api.patch_interface(nombre, **campos)
        print(f"   ✅ {nombre} actualizada: {', '.join(campos)}")
        cambios += 1

    return cambios


def main(dry_run: bool = False, estricto: bool = False) -> int:
    print("-> Reconciliacion declarativa contra API REST")
    print(f"   modo: {'DRY-RUN (no aplica nada)' if dry_run else 'APLICAR'}"
          f"{' + ESTRICTO (borra deriva)' if estricto else ''}")

    # FASE 0 · cargar el modelo
    try:
        deseado = cargar_modelo(MODELO, HOSTNAME)
    except FileNotFoundError:
        print(f"❌ No se encontro {MODELO}")
        return 1
    except KeyError as e:
        print(f"❌ {e}")
        return 1

    with RestClient(base_url=datos_device["base_url"],
                    verificar_tls=datos_device["verificar_tls"]) as api:
        try:
            api.login(datos_device["usuario"], datos_device["password"])

            # FASE 1 · leer el estado real
            print(f"{'\n'}-> Leyendo estado actual de {HOSTNAME}...")
            vlans_reales = api.get_vlans()
            interfaces_reales = api.get_interfaces()
            print(f"   {len(vlans_reales)} VLANs, {len(interfaces_reales)} interfaces")

            # FASE 2 · calcular el plan (nada se modifica todavia)
            print(f"{'\n'}-> Plan de cambios:")
            plan = calcular_plan(deseado, vlans_reales, interfaces_reales)
            plan.mostrar(estricto)

            pendientes = plan.a_aplicar(estricto)

            if dry_run:
                print(f"{'\n'}-> DRY-RUN: se habrian aplicado {pendientes} cambios.")
                return 0

            if pendientes == 0:
                # Puede haber deriva reportada y aun asi no haber nada que
                # aplicar: eso es correcto y tiene que dar changed=0.
                print(f"{'\n'}-> changed=0  ✅ la realidad ya coincide con el modelo")
                return 0

            # FASE 3 · aplicar
            print(f"{'\n'}-> Aplicando...")
            cambios = aplicar_plan(api, plan, estricto)
            print(f"{'\n'}-> changed={cambios}")

        except RestError as error:
            print(f"{'\n'}❌ {error}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(dry_run="--dry-run" in sys.argv,
                          estricto="--estricto" in sys.argv))
