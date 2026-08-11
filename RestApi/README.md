# Network Automation with REST API and RESTCONF

**Author:** Ed Scrimaglia
**Version:** 1.0
**Project:** Consuming network APIs with Python `requests`
**Creation Date:** March 2026

---

## Project Description

This project closes the course by showing the same problem as the previous sections —taking a data
model to a device's configuration— solved over **HTTP** instead of SSH.

The central difference: a REST API returns **structured data** and **explicit status codes**. There
is no text to parse (TextFSM) and no looking for `% Invalid input` in the output: the device answers
`201`, `409` or `422`, and the meaning is defined by the protocol.

**It includes a controller simulator** (`mock_server.py`), so every example can be run and verified
**without hardware and without access to a real device**.

---

## Main Features

- Reusable `RestClient` class with a persistent HTTP session, token and retries
- Translation of HTTP errors into a single `RestError` exception
- Idempotency by design: `409 Conflict` and `404 Not Found` treated as success where appropriate
- Declarative reconciliation: read real state → compute plan → apply only the difference
- `--dry-run` mode (the equivalent of Ansible's `--check`)
- `--estricto` mode, which **removes configuration drift**
- RESTCONF client for YANG models
- Controller simulator with automatic OpenAPI documentation

---

## Dependencies

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

The `mock` group is only needed for the simulator. To talk to a real device, `requests` and `pyyaml`
are enough.

```bash
uv sync --extra mock
```

---

## Project Structure

```tree
RestApi/
├── pyproject.toml          # Project dependencies
├── README.md               # This file
├── mock_server.py          # Network controller simulator (FastAPI)
├── rest_clase.py           # RestClient class + RestError exception
├── datos_device.py         # Connection parameters (from environment variables)
├── modelo_datos.yaml       # Source of Truth (same one as the Ansible module)
├── rest_eje1.py            # Example 1: authentication and queries
├── rest_eje2.py            # Example 2: changes, status codes, idempotency
├── rest_eje3.py            # Example 3: RESTCONF / YANG
└── integrador3.py          # Integrator: model → API with reconciliation
```

---

## Usage

### 1. Start the simulator

In one terminal, and leave it open:

```bash
uv run --extra mock python mock_server.py
```

The scripts in this module print in Spanish; their output is shown verbatim:

```text
-> Mock Network Controller en http://127.0.0.1:8443
-> Documentacion OpenAPI en http://127.0.0.1:8443/docs
```

Open `http://127.0.0.1:8443/docs` in the browser: FastAPI generates the API's interactive
documentation from the code. It is a good way to explore the endpoints before programming against
them.

### 2. Run the examples

In another terminal:

```bash
uv run python rest_eje1.py          # authentication and queries
uv run python rest_eje2.py          # changes and idempotency
uv run python rest_eje3.py          # RESTCONF
```

> ⚠️ **The simulator's state lives in memory and the examples modify it.**
> `rest_eje2.py` changes VLAN 30 and interface `Gi1/2`, so if it is run before the integrator, the
> change plan will differ from the one this README shows. To reproduce the documented output
> exactly, **restart the simulator** (Ctrl-C and start it again) before each sequence.
>
> This is a deliberate limitation: a simulator without persistence resets in a second, which is
> exactly what you want for testing. Its equivalent in the course lab is the chapter 2 snapshot.

### 3. The integrator

```bash
uv run python integrador3.py --dry-run     # simulates, changes nothing
uv run python integrador3.py               # applies
uv run python integrador3.py               # second run → changed=0
uv run python integrador3.py --estricto    # also removes drift
```

### 4. Against a real device

Credentials and the URL come from environment variables, not from the code:

```bash
export NET_API_URL="https://10.2.0.200"
export NET_API_USER="automation"
export NET_API_PASS="$(security find-generic-password -s net-api -w)"
export NET_API_TLS="true"

uv run python integrador3.py --dry-run
```

---

## Components

### `rest_clase.py` — the `RestClient` class

| Method | Description |
|---|---|
| `login(usuario, password)` | Gets the token and leaves it in the session |
| `logout()` | Closes the session (does not raise on failure) |
| `get_system()` | Device data — equivalent of `show version` |
| `get_vlans()` | `{vlan_id: name}` — equivalent of `show vlan brief` |
| `get_interfaces()` | `{name: {...}}` — equivalent of `show ip int brief` |
| `create_vlan(id, nombre)` | POST. Accepts `409` as success |
| `rename_vlan(id, nombre)` | PUT. Idempotent by definition |
| `delete_vlan(id)` | DELETE. Accepts `404` as success |
| `patch_interface(nombre, **campos)` | Partial PATCH of an interface |
| `restconf_get(ruta_yang)` | GET with `Accept: application/yang-data+json` |

**Design decisions**, made by correcting the antipatterns found in the previous modules:

- **It does not call `exit()`**: it raises `RestError` and `main` decides (unlike the classes in
  `Netmiko/sim_caso`).
- **It is a context manager**: `with RestClient(...) as api:` guarantees the `logout`, just like
  `ConnectHandler`'s `with`.
- **A single TCP session**, reused, with `requests.Session()`.
- **Retries only on idempotent methods** (`GET`, `PUT`, `DELETE`). Never on `POST`.
- **A single place that speaks HTTP** (`_request`), where every error is translated.

### `integrador3.py` — declarative reconciliation

```text
FASE 0 · cargar el modelo         ← Source of Truth
FASE 1 · leer el estado real      ← GET
FASE 2 · calcular el plan         ← diff, sin tocar nada
FASE 3 · aplicar solo lo que falta ← POST / PUT / PATCH / DELETE
```

The `dataclass Plan` is the structured equivalent of the `.cfg` file from the previous modules: the
reviewable artifact you inspect before applying.

---

## Expected output

### `integrador3.py --dry-run` (first time)

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

### `integrador3.py` (apply, then the idempotency test)

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

## HTTP status codes and their meaning in networking

| Code | Meaning | What to do |
|---|---|---|
| `200 OK` | The query succeeded | continue |
| `201 Created` | The resource was created | continue, count as `changed` |
| `204 No Content` | It was deleted; there is no response body | continue |
| `400 Bad Request` | The request is malformed | review the JSON sent |
| `401 Unauthorized` | Token missing, invalid or expired | authenticate again |
| `403 Forbidden` | Authenticated, but forbidden by policy | do not retry |
| `404 Not Found` | The resource does not exist | on a DELETE, it is success |
| `409 Conflict` | The resource already exists | on a POST, it is success |
| `422 Unprocessable` | Valid syntax, invalid state or value | review the data model |
| `429 Too Many Requests` | Rate limiting | retry with backoff |
| `5xx` | Device problem | retry with backoff |

The two that make idempotency possible are **`409`** and **`404`**.

---

## Troubleshooting

### `RestError: HTTP 0 ... No se pudo conectar`

The simulator is not running, or the URL is wrong. Verify:

```bash
curl -s http://127.0.0.1:8443/docs -o /dev/null -w "%{http_code}\n"
```

### `HTTP 404 on PATCH .../interfaces/GigabitEthernet1/2`

The interface name contains a slash, which cuts the HTTP path. The server has to declare the
parameter as `{name:path}`, or the client has to encode the slash as `%2F`. It is a real and
frequent problem with interface names.

### `HTTP 401: Token invalido o expirado`

The token expired. In production it has to be renewed; the usual pattern is to intercept the `401`,
authenticate again once, and retry the request.

### `SSLError: certificate verify failed`

Self-signed certificate. In the lab: `NET_API_TLS=false`. In production: install your own CA,
**never** disable verification.

---

## Proposed exercises

1. Add `get_vlan(vlan_id)` to the class and use it to verify each creation.
2. Implement automatic token renewal on a `401`.
3. Validate `modelo_datos.yaml` with JSON Schema before phase 1 (reuse
   `Modelado/main_schema.py`).
4. Add reconciliation of the `allowed_vlans` on trunk interfaces.
5. Write the plan to a JSON file, so it remains a versionable artifact.
6. Measure total time, as `Netmiko/sim_caso/main.py` does.
7. Add a VLANs endpoint to the simulator that returns `429` one out of every three times, and check
   that the retry policy handles it.

---

## References

- [Requests](https://requests.readthedocs.io/)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [RFC 8040 — RESTCONF](https://www.rfc-editor.org/rfc/rfc8040.html)
- [RFC 7950 — YANG 1.1](https://www.rfc-editor.org/rfc/rfc7950.html)
- [Cisco IOS-XE RESTCONF](https://developer.cisco.com/docs/ios-xe/#!restconf)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## License

Educational project - UTN-FRC Cisco Academy - Network Automation Engineer Course

---

**Last updated**: March 2026
