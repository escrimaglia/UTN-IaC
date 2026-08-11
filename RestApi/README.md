# Automatización de Redes con REST API y RESTCONF

**Autor:** Ed Scrimaglia
**Versión:** 1.0
**Proyecto:** Consumo de APIs de red con Python `requests`
**Fecha de Creación:** Marzo de 2026

---

## Descripción del Proyecto

Este proyecto cierra el curso mostrando el mismo problema de las secciones anteriores —llevar un
modelo de datos a la configuración de un equipo— resuelto sobre **HTTP** en lugar de SSH.

La diferencia central: una API REST devuelve **datos estructurados** y **códigos de estado
explícitos**. No hay que parsear texto (TextFSM) ni buscar `% Invalid input` en la salida: el
equipo responde `201`, `409` o `422` y el significado está definido por el protocolo.

**Incluye un simulador de controlador** (`mock_server.py`), de modo que todos los ejemplos se pueden
ejecutar y verificar **sin hardware y sin acceso a un equipo real**.

---

## Características Principales

- Clase reutilizable `RestClient` con sesión HTTP persistente, token y reintentos
- Traducción de errores HTTP a una única excepción `RestError`
- Idempotencia por diseño: `409 Conflict` y `404 Not Found` tratados como éxito cuando corresponde
- Reconciliación declarativa: leer estado real → calcular plan → aplicar solo la diferencia
- Modo `--dry-run` (el equivalente del `--check` de Ansible)
- Modo `--estricto` que **elimina deriva de configuración**
- Cliente RESTCONF para modelos YANG
- Simulador de controlador con documentación OpenAPI automática

---

## Dependencias

```toml
[project]
dependencies = [
    "requests>=2.32.0",
    "pyyaml>=6.0.3",
    "jsonschema>=4.25.1",
]

[project.optional-dependencies]
mock = ["fastapi>=0.115.0", "uvicorn>=0.32.0"]
```

El grupo `mock` solo hace falta para el simulador. Para hablar con un equipo real, `requests` y
`pyyaml` alcanzan.

```bash
uv sync --extra mock
```

---

## Estructura del Proyecto

```tree
RestApi/
├── pyproject.toml          # Dependencias del proyecto
├── README.md               # Este archivo
├── mock_server.py          # Simulador de controlador de red (FastAPI)
├── rest_clase.py           # Clase RestClient + excepción RestError
├── datos_device.py         # Parámetros de conexión (desde variables de entorno)
├── modelo_datos.yaml       # Source of Truth (mismo del módulo Ansible)
├── rest_eje1.py            # Ejemplo 1: autenticación y consultas
├── rest_eje2.py            # Ejemplo 2: cambios, códigos de estado, idempotencia
├── rest_eje3.py            # Ejemplo 3: RESTCONF / YANG
└── integrador3.py          # Integrador: modelo → API con reconciliación
```

---

## Uso

### 1. Levantar el simulador

En una terminal, y dejarla abierta:

```bash
uv run --extra mock python mock_server.py
```

```text
-> Mock Network Controller en http://127.0.0.1:8443
-> Documentacion OpenAPI en http://127.0.0.1:8443/docs
```

Abrir `http://127.0.0.1:8443/docs` en el navegador: FastAPI genera la documentación interactiva de
la API a partir del código. Es una buena manera de explorar los endpoints antes de programar contra
ellos.

### 2. Ejecutar los ejemplos

En otra terminal:

```bash
uv run python rest_eje1.py          # autenticación y consultas
uv run python rest_eje2.py          # cambios e idempotencia
uv run python rest_eje3.py          # RESTCONF
```

> ⚠️ **El estado del simulador vive en memoria y los ejemplos lo modifican.**
> `rest_eje2.py` cambia la VLAN 30 y la interfaz `Gi1/2`, así que si se corre antes del integrador,
> el plan de cambios va a ser distinto del que muestra este README. Para reproducir exactamente las
> salidas documentadas, **reiniciar el simulador** (Ctrl-C y volver a levantarlo) antes de cada
> secuencia.
>
> Es una limitación deliberada: un simulador sin persistencia se vuelve a cero en un segundo, lo que
> es exactamente lo que se quiere para probar. El equivalente en el laboratorio del curso es el
> snapshot del capítulo 2.

### 3. El integrador

```bash
uv run python integrador3.py --dry-run     # simula, no cambia nada
uv run python integrador3.py               # aplica
uv run python integrador3.py               # segunda corrida → changed=0
uv run python integrador3.py --estricto    # además elimina la deriva
```

### 4. Contra un equipo real

Las credenciales y la URL salen de variables de entorno, no del código:

```bash
export NET_API_URL="https://10.2.0.200"
export NET_API_USER="automation"
export NET_API_PASS="$(security find-generic-password -s net-api -w)"
export NET_API_TLS="true"

uv run python integrador3.py --dry-run
```

---

## Componentes

### `rest_clase.py` — la clase `RestClient`

| Método | Descripción |
|---|---|
| `login(usuario, password)` | Obtiene el token y lo deja en la sesión |
| `logout()` | Cierra la sesión (no lanza si falla) |
| `get_system()` | Datos del equipo — equivalente de `show version` |
| `get_vlans()` | `{vlan_id: nombre}` — equivalente de `show vlan brief` |
| `get_interfaces()` | `{nombre: {...}}` — equivalente de `show ip int brief` |
| `create_vlan(id, nombre)` | POST. Acepta `409` como éxito |
| `rename_vlan(id, nombre)` | PUT. Idempotente por definición |
| `delete_vlan(id)` | DELETE. Acepta `404` como éxito |
| `patch_interface(nombre, **campos)` | PATCH parcial de una interfaz |
| `restconf_get(ruta_yang)` | GET con `Accept: application/yang-data+json` |

**Decisiones de diseño**, tomadas corrigiendo los antipatrones detectados en los módulos anteriores:

- **No llama a `exit()`**: lanza `RestError` y el `main` decide (a diferencia de las clases de
  `Netmiko/sim_caso`).
- **Es context manager**: `with RestClient(...) as api:` garantiza el `logout`, igual que el `with`
  de `ConnectHandler`.
- **Una sola sesión TCP** reutilizada, con `requests.Session()`.
- **Reintentos solo en métodos idempotentes** (`GET`, `PUT`, `DELETE`). Nunca en `POST`.
- **Un único punto que habla HTTP** (`_request`), donde se traducen todos los errores.

### `integrador3.py` — reconciliación declarativa

```text
FASE 0 · cargar el modelo         ← Source of Truth
FASE 1 · leer el estado real      ← GET
FASE 2 · calcular el plan         ← diff, sin tocar nada
FASE 3 · aplicar solo lo que falta ← POST / PUT / PATCH / DELETE
```

La `dataclass Plan` es el equivalente estructurado del archivo `.cfg` de los módulos anteriores: el
artefacto revisable que se inspecciona antes de aplicar.

---

## Salida esperada

### `integrador3.py --dry-run` (primera vez)

```text
-> Reconciliacion declarativa contra API REST
   modo: DRY-RUN (no aplica nada)

-> Leyendo estado actual de SW-Bld_A...
   4 VLANs, 4 interfaces

-> Plan de cambios:
   + VLAN 30 'Finanzas'
   ! VLAN 99 'VLAN_del_proveedor_de_telefonia' no esta en el modelo   (deriva: usar --estricto para borrarla)
   ~ GigabitEthernet1/2: description: 'puerto libre' → 'Conexion a PC_PROD_1', vlan: 1 → 20, enabled: False → True

-> DRY-RUN: se habrian aplicado 2 cambios.
```

### `integrador3.py` (aplicar, y después la prueba de idempotencia)

```text
-> Aplicando...
   ✅ VLAN 30 'Finanzas' creada
   ✅ GigabitEthernet1/2 actualizada: description, vlan, enabled

-> changed=2
```

```text
-> Plan de cambios:
   ! VLAN 99 'VLAN_del_proveedor_de_telefonia' no esta en el modelo   (deriva: usar --estricto para borrarla)

-> changed=0  ✅ la realidad ya coincide con el modelo
```

### `integrador3.py --estricto`

```text
-> Plan de cambios:
   - VLAN 99 'VLAN_del_proveedor_de_telefonia' no esta en el modelo

-> Aplicando...
   ✅ VLAN 99 'VLAN_del_proveedor_de_telefonia' eliminada (deriva)

-> changed=1
```

---

## Códigos de estado HTTP y su significado en redes

| Código | Significado | Qué hacer |
|---|---|---|
| `200 OK` | La consulta salió bien | seguir |
| `201 Created` | El recurso se creó | seguir, contar como `changed` |
| `204 No Content` | Se borró; no hay cuerpo de respuesta | seguir |
| `400 Bad Request` | La petición está mal formada | revisar el JSON enviado |
| `401 Unauthorized` | Token ausente, inválido o expirado | volver a autenticar |
| `403 Forbidden` | Autenticado, pero prohibido por política | no reintentar |
| `404 Not Found` | El recurso no existe | en un DELETE, es éxito |
| `409 Conflict` | El recurso ya existe | en un POST, es éxito |
| `422 Unprocessable` | Sintaxis válida, estado o valor inválido | revisar el modelo de datos |
| `429 Too Many Requests` | Rate limiting | reintentar con backoff |
| `5xx` | Problema del equipo | reintentar con backoff |

Los dos que hacen posible la idempotencia son **`409`** y **`404`**.

---

## Troubleshooting

### `RestError: HTTP 0 ... No se pudo conectar`

El simulador no está corriendo, o la URL es incorrecta. Verificar:

```bash
curl -s http://127.0.0.1:8443/docs -o /dev/null -w "%{http_code}\n"
```

### `HTTP 404 en PATCH .../interfaces/GigabitEthernet1/2`

El nombre de la interfaz contiene una barra, que corta la ruta HTTP. El servidor tiene que declarar
el parámetro como `{name:path}`, o el cliente tiene que codificar la barra como `%2F`. Es un
problema real y frecuente con nombres de interfaz.

### `HTTP 401: Token invalido o expirado`

El token venció. En producción hay que renovarlo; el patrón habitual es interceptar el `401`,
volver a autenticar una vez y reintentar la petición.

### `SSLError: certificate verify failed`

Certificado autofirmado. En laboratorio: `NET_API_TLS=false`. En producción: instalar el CA propio,
**nunca** desactivar la verificación.

---

## Ejercicios propuestos

1. Agregar `get_vlan(vlan_id)` a la clase y usarla para verificar cada creación.
2. Implementar renovación automática de token ante un `401`.
3. Validar `modelo_datos.yaml` con JSON Schema antes de la fase 1 (reutilizar
   `Modelado/main_schema.py`).
4. Agregar reconciliación de los `allowed_vlans` de las interfaces trunk.
5. Escribir el plan a un archivo JSON, para que quede como artefacto versionable.
6. Medir el tiempo total, como hace `Netmiko/sim_caso/main.py`.
7. Agregar un endpoint de VLANs al simulador que devuelva `429` una vez de cada tres, y comprobar
   que la política de reintentos lo maneja.

---

## Referencias

- [Requests](https://requests.readthedocs.io/)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 8040 — RESTCONF](https://www.rfc-editor.org/rfc/rfc8040.html)
- [RFC 7950 — YANG 1.1](https://www.rfc-editor.org/rfc/rfc7950.html)
- [Cisco IOS-XE RESTCONF](https://developer.cisco.com/docs/ios-xe/#!restconf)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## Licencia

Proyecto educativo - UTN-FRC Academia Cisco - Network Automation Engineer Course

---

**Última actualización**: Marzo 2026
