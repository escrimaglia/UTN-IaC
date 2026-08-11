# Ejemplo 3: RESTCONF. El mismo equipo, con datos modelados en YANG.
# By Ed Scrimaglia

import json
from rest_clase import RestClient, RestError
from datos_device import datos_device


def main() -> int:
    with RestClient(base_url=datos_device["base_url"],
                    verificar_tls=datos_device["verificar_tls"]) as api:
        try:
            api.login(datos_device["usuario"], datos_device["password"])

            # La ruta RESTCONF codifica el modelo YANG y el contenedor:
            #   /restconf/data/<modulo-yang>:<contenedor>
            datos = api.restconf_get("ietf-interfaces:interfaces")

            print("-> Respuesta RESTCONF cruda:")
            print(json.dumps(datos, indent=3))

            # La clave de nivel superior lleva el nombre del modulo YANG.
            # Eso hace la respuesta autodescriptiva: se sabe QUE modelo la define.
            interfaces = datos["ietf-interfaces:interfaces"]["interface"]

            print(f"{'\n'}-> {len(interfaces)} interfaces segun ietf-interfaces:")
            for inter in interfaces:
                estado = "enabled" if inter["enabled"] else "disabled"
                print(f"   {inter['name']:<22} {estado:<9} {inter['description']}")

            print(f"{'\n'}-> Diferencia clave con la CLI:")
            print("   el nombre del modulo YANG viaja en la respuesta.")
            print("   No hay que adivinar el formato: esta especificado.")

        except RestError as error:
            print(f"{'\n'}❌ {error}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
