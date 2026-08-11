# Prueba un template TextFSM contra un archivo, sin conectarse a ningun equipo.
#
# El metodo es el del capitulo 9 §9.4 del libro: guardar la salida real una sola
# vez en un archivo y trabajar contra el archivo. Un template se escribe en unas
# diez iteraciones, y hacer diez conexiones SSH para eso es tiempo perdido.
#
# salida_trunk.txt no es un archivo temporal: versionado, es el caso de prueba
# del template. El dia que una actualizacion de IOS cambie el formato, esto falla
# en el pipeline en lugar de fallar en produccion.
#
# Uso:
#   uv run python probar_template.py

import json
import textfsm
from pathlib import Path

AQUI = Path(__file__).parent
TEMPLATE = AQUI / "cisco_ios_show_interfaces_trunk.textfsm"
SALIDA = AQUI / "salida_trunk.txt"

# Lo que el template tiene que devolver para salida_trunk.txt. Es la parte que
# convierte este script en un test y no solo en una demostracion.
ESPERADO = [
    {"PORT": "Gi0/1", "VLANS_PERMITIDAS": "10,20"},
    {"PORT": "Gi0/2", "VLANS_PERMITIDAS": "10,20"},
]


def main() -> int:
    with open(TEMPLATE) as f:
        fsm = textfsm.TextFSM(f)

    with open(SALIDA) as f:
        filas = fsm.ParseText(f.read())

    obtenido = [dict(zip(fsm.header, fila)) for fila in filas]

    print(fsm.header)
    print(json.dumps(obtenido, indent=2))

    if obtenido == ESPERADO:
        print(f"\n-> OK: {len(obtenido)} filas, como se esperaba")
        return 0

    print(f"\n-> FALLO: se esperaban {len(ESPERADO)} filas y salieron {len(obtenido)}")
    print(f"   esperado: {ESPERADO}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
