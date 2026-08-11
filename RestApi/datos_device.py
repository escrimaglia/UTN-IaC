# Parametros de conexion al controlador.
# En produccion, las credenciales salen de variables de entorno o de un
# gestor de secretos (cap. 17), nunca de este archivo.

import os

datos_device = {
    "base_url": os.getenv("NET_API_URL", "http://127.0.0.1:8443"),
    "usuario": os.getenv("NET_API_USER", "netsim"),
    "password": os.getenv("NET_API_PASS", "password"),
    # En el laboratorio con certificado autofirmado: False.
    # En produccion: True, o la ruta al CA propio.
    "verificar_tls": os.getenv("NET_API_TLS", "false").lower() == "true",
}
