# Simulador de un controlador de red con API REST.
# Permite ejecutar y verificar todos los ejemplos del capitulo sin hardware.
# By Ed Scrimaglia
#
# Uso:
#   uv run --extra mock python mock_server.py
#   (queda escuchando en http://127.0.0.1:8443)

from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, Field
from typing import Annotated
import secrets
import uvicorn

app = FastAPI(title="Mock Network Controller", version="1.0")

# ─── Estado en memoria: simula la configuracion del equipo ──────────────
USUARIO = "netsim"
PASSWORD = "password"
TOKENS: set[str] = set()

VLANS: dict[int, str] = {
    1: "default",                            # ← existe en todo switch, no se borra
    10: "Ingenieria",
    20: "Produccion",
    99: "VLAN_del_proveedor_de_telefonia",   # ← deriva de configuracion (cap. 21)
}

INTERFACES: dict[str, dict] = {
    "GigabitEthernet0/1": {"description": "Conexion a SW-CORE_1", "mode": "trunk",
                           "allowed_vlans": [10, 20], "vlan": None, "enabled": True},
    "GigabitEthernet0/2": {"description": "Conexion a SW-CORE_2", "mode": "trunk",
                           "allowed_vlans": [10, 20], "vlan": None, "enabled": True},
    "GigabitEthernet1/1": {"description": "Conexion a PC_ING_1", "mode": "access",
                           "allowed_vlans": None, "vlan": 10, "enabled": True},
    "GigabitEthernet1/2": {"description": "puerto libre", "mode": "access",
                           "allowed_vlans": None, "vlan": 1, "enabled": False},
}


# ─── Modelos de entrada (Pydantic valida por nosotros) ──────────────────
class Credenciales(BaseModel):
    username: str
    password: str


class VlanIn(BaseModel):
    vlan_id: Annotated[int, Field(ge=1, le=4094)]
    name: Annotated[str, Field(min_length=1, max_length=32)]


class VlanUpdate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=32)]


class InterfaceUpdate(BaseModel):
    description: str | None = None
    mode: str | None = None
    vlan: int | None = None
    enabled: bool | None = None


def _auth(token: str | None) -> None:
    """Valida el token. Lanza 401 si no sirve."""
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta el header Authorization")
    if token.removeprefix("Bearer ") not in TOKENS:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")


# ─── Autenticacion ─────────────────────────────────────────────────────
@app.post("/api/v1/login")
def login(cred: Credenciales):
    if cred.username != USUARIO or cred.password != PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = secrets.token_hex(16)
    TOKENS.add(token)
    return {"token": token, "expires_in": 3600}


@app.post("/api/v1/logout", status_code=204)
def logout(authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    TOKENS.discard(authorization.removeprefix("Bearer "))
    return Response(status_code=204)


# ─── Sistema ───────────────────────────────────────────────────────────
@app.get("/api/v1/system")
def system(authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    return {"hostname": "SW-Bld_A", "model": "vios_l2",
            "version": "15.2(CML)", "uptime_seconds": 4332}


# ─── VLANs ─────────────────────────────────────────────────────────────
@app.get("/api/v1/vlans")
def list_vlans(authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    return {"vlans": [{"vlan_id": k, "name": v} for k, v in sorted(VLANS.items())]}


@app.get("/api/v1/vlans/{vlan_id}")
def get_vlan(vlan_id: int, authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    if vlan_id not in VLANS:
        raise HTTPException(status_code=404, detail=f"VLAN {vlan_id} no existe")
    return {"vlan_id": vlan_id, "name": VLANS[vlan_id]}


@app.post("/api/v1/vlans", status_code=201)
def create_vlan(vlan: VlanIn, authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    if vlan.vlan_id in VLANS:
        # 409 Conflict: el recurso ya existe. Clave para la idempotencia.
        raise HTTPException(status_code=409,
                            detail=f"VLAN {vlan.vlan_id} ya existe con nombre "
                                   f"'{VLANS[vlan.vlan_id]}'")
    VLANS[vlan.vlan_id] = vlan.name
    return {"vlan_id": vlan.vlan_id, "name": vlan.name}


@app.put("/api/v1/vlans/{vlan_id}")
def update_vlan(vlan_id: int, cambio: VlanUpdate,
                authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    if vlan_id not in VLANS:
        raise HTTPException(status_code=404, detail=f"VLAN {vlan_id} no existe")
    VLANS[vlan_id] = cambio.name
    return {"vlan_id": vlan_id, "name": cambio.name}


@app.delete("/api/v1/vlans/{vlan_id}", status_code=204)
def delete_vlan(vlan_id: int, authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    if vlan_id not in VLANS:
        raise HTTPException(status_code=404, detail=f"VLAN {vlan_id} no existe")
    if vlan_id == 1:
        raise HTTPException(status_code=403, detail="No se puede borrar la VLAN 1")
    del VLANS[vlan_id]
    return Response(status_code=204)


# ─── Interfaces ────────────────────────────────────────────────────────
@app.get("/api/v1/interfaces")
def list_interfaces(authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    return {"interfaces": [{"name": k, **v} for k, v in INTERFACES.items()]}


# El nombre de una interfaz contiene barras ("GigabitEthernet1/2"), asi que el
# parametro de ruta se declara como {name:path}. Sin el ':path', la barra corta
# la ruta y el resultado es un 404 desconcertante. Ver cap. 19 §19.3.
@app.patch("/api/v1/interfaces/{name:path}")
def patch_interface(name: str, cambio: InterfaceUpdate,
                    authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    if name not in INTERFACES:
        raise HTTPException(status_code=404, detail=f"Interfaz {name} no existe")
    nuevo = cambio.model_dump(exclude_none=True)
    if nuevo.get("mode") == "access" and "vlan" in nuevo:
        if nuevo["vlan"] not in VLANS:
            # El equipo se niega: sintaxis correcta, estado invalido.
            raise HTTPException(status_code=422,
                                detail=f"La VLAN {nuevo['vlan']} no existe en el equipo")
    INTERFACES[name].update(nuevo)
    return {"name": name, **INTERFACES[name]}


# ─── RESTCONF: mismo equipo, estilo YANG ───────────────────────────────
@app.get("/restconf/data/ietf-interfaces:interfaces")
def restconf_interfaces(authorization: Annotated[str | None, Header()] = None):
    _auth(authorization)
    return {
        "ietf-interfaces:interfaces": {
            "interface": [
                {"name": name,
                 "description": data["description"],
                 "type": "iana-if-type:ethernetCsmacd",
                 "enabled": data["enabled"]}
                for name, data in INTERFACES.items()
            ]
        }
    }


if __name__ == "__main__":
    print("-> Mock Network Controller en http://127.0.0.1:8443")
    print("-> Documentacion OpenAPI en http://127.0.0.1:8443/docs")
    uvicorn.run(app, host="127.0.0.1", port=8443, log_level="warning")
