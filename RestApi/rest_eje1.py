# Ejemplo 1: autenticacion, token y consultas.
# El equivalente de netmiko_eje1.py, pero sobre HTTP.
# By Ed Scrimaglia

import json
from rest_clase import RestClient, RestError
from datos_device import datos_device


def main() -> int:
    # El 'with' garantiza el logout, como en Netmiko garantizaba el disconnect
    with RestClient(base_url=datos_device["base_url"],
                    verificar_tls=datos_device["verificar_tls"]) as api:
        try:
            api.login(datos_device["usuario"], datos_device["password"])
            print(f"-> Sesion establecida. Token: {api.token[:8]}...")

            # 1 · Datos del sistema: el equivalente de 'show version'
            sistema = api.get_system()
            print(f"{'\n'}-> Sistema:")
            print(json.dumps(sistema, indent=3))
            print(f"   Hostname: {sistema.get('hostname')}")
            print(f"   Version:  {sistema.get('version')}")

            # 2 · VLANs: el equivalente de 'show vlan brief'.
            #     Notar que NO hay que parsear nada.
            vlans = api.get_vlans()
            print(f"{'\n'}-> VLANs configuradas ({len(vlans)}):")
            for vlan_id, nombre in sorted(vlans.items()):
                print(f"   {vlan_id:>4}  {nombre}")

            # 3 · Interfaces: el equivalente de 'show ip interface brief'
            interfaces = api.get_interfaces()
            print(f"{'\n'}-> Interfaces ({len(interfaces)}):")
            for nombre, datos in interfaces.items():
                estado = "up" if datos["enabled"] else "down"
                detalle = (f"vlan {datos['vlan']}" if datos["mode"] == "access"
                           else f"trunk {datos['allowed_vlans']}")
                print(f"   {nombre:<22} {datos['mode']:<7} {detalle:<18} {estado}")

        except RestError as error:
            # Un solo except para toda la familia de errores HTTP
            print(f"{'\n'}❌ {error}")
            return 1

    print(f"{'\n'}-> Sesion cerrada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
