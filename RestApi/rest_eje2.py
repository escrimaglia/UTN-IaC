# Ejemplo 2: cambios, codigos de estado e idempotencia.
# El equivalente de netmiko_eje1.py de ejemplo2 (send_config_set), sobre HTTP.
# By Ed Scrimaglia

from rest_clase import RestClient, RestError
from datos_device import datos_device


def separador(titulo: str) -> None:
    print(f"{'\n'}{'─' * 62}{'\n'}{titulo}{'\n'}{'─' * 62}")


def main() -> int:
    with RestClient(base_url=datos_device["base_url"],
                    verificar_tls=datos_device["verificar_tls"]) as api:
        try:
            api.login(datos_device["usuario"], datos_device["password"])

            separador("1 · CREAR: 201 la primera vez, 409 la segunda")
            # POST no es idempotente por definicion. El truco esta en aceptar
            # el 409 (Conflict) como exito: significa 'ya existe'.
            for intento in (1, 2):
                api.create_vlan(30, "Finanzas")
                print(f"   intento {intento}: VLAN 30 creada o ya existente ✅")
            print("   → el script se puede reintentar sin miedo (principio 5)")

            separador("2 · MODIFICAR: PUT es idempotente por definicion")
            for intento in (1, 2):
                r = api.rename_vlan(30, "Finanzas_y_Contabilidad")
                print(f"   intento {intento}: name = '{r['name']}'")
            print("   → PUT reemplaza el recurso: dos veces = una vez")

            separador("3 · BORRAR: 204 la primera vez, 404 la segunda")
            for intento in (1, 2):
                api.delete_vlan(30)
                print(f"   intento {intento}: VLAN 30 ausente ✅")

            separador("4 · ERRORES QUE EL EQUIPO RECHAZA")

            # 4a · el equipo valida el rango: 4095 esta fuera
            try:
                api.create_vlan(4095, "Invalida")
            except RestError as e:
                print(f"   422 rango invalido → {e.status}: {e.detalle[:70]}...")

            # 4b · estado invalido: la interfaz pide una VLAN que no existe
            try:
                api.patch_interface("GigabitEthernet1/2", mode="access", vlan=777)
            except RestError as e:
                print(f"   422 estado invalido → {e.status}: {e.detalle}")

            # 4c · recurso inexistente
            try:
                api.rename_vlan(888, "Fantasma")
            except RestError as e:
                print(f"   404 no existe      → {e.status}: {e.detalle}")

            # 4d · prohibido por politica del equipo
            try:
                api.delete_vlan(1)
            except RestError as e:
                print(f"   403 prohibido      → {e.status}: {e.detalle}")

            print(f"{'\n'}   → cuatro fallos distintos, cuatro codigos distintos.")
            print("     Con la CLI, los cuatro son texto que hay que buscar.")

            separador("5 · UN CAMBIO QUE SI FUNCIONA")
            r = api.patch_interface("GigabitEthernet1/2",
                                    description="Conexion a PC_PROD_1",
                                    mode="access", vlan=20, enabled=True)
            print(f"   {r['name']}: {r['description']}")
            print(f"   mode={r['mode']} vlan={r['vlan']} enabled={r['enabled']} ✅")

        except RestError as error:
            print(f"{'\n'}❌ Error no esperado: {error}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
