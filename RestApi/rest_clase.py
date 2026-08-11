# Clase para automatizacion de dispositivos de red via API REST.
# Equivalente de NetmikoInicial / ConfigurationClass, pero sobre HTTP.
# By Ed Scrimaglia

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RestError(Exception):
    """Error de la API. Lleva el codigo de estado y el detalle del equipo."""

    def __init__(self, status: int, detalle: str, metodo: str, url: str):
        self.status = status
        self.detalle = detalle
        self.metodo = metodo
        self.url = url
        super().__init__(f"HTTP {status} en {metodo} {url}: {detalle}")


class RestClient:
    """Cliente REST para un controlador de red.

    A diferencia de las clases de Netmiko del curso, esta NO llama a exit():
    lanza RestError y el main decide que hacer (cap. 12, correccion 5).
    """

    def __init__(self, base_url: str, verificar_tls: bool = True,
                 timeout: int = 10, reintentos: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None

        # Una sola sesion TCP reutilizada para todas las peticiones.
        # Es el equivalente de reutilizar la conexion SSH (cap. 8).
        self.session = requests.Session()
        self.session.verify = verificar_tls

        # Reintenta solo los errores transitorios y solo en metodos seguros.
        politica = Retry(
            total=reintentos,
            backoff_factor=0.5,                       # 0.5s, 1s, 2s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "DELETE"],  # NO POST: no es idempotente
        )
        adaptador = HTTPAdapter(max_retries=politica)
        self.session.mount("https://", adaptador)
        self.session.mount("http://", adaptador)

    # ─── Contexto: garantiza el logout ─────────────────────────────────
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.logout()
        self.session.close()
        return False

    # ─── Autenticacion ────────────────────────────────────────────────
    def login(self, usuario: str, password: str) -> str:
        """Obtiene el token y lo deja en la sesion."""
        datos = self._request("POST", "/api/v1/login",
                              json={"username": usuario, "password": password},
                              autenticar=False)
        self.token = datos["token"]
        self.session.headers["Authorization"] = f"Bearer {self.token}"
        return self.token

    def logout(self) -> None:
        if not self.token:
            return
        try:
            self._request("POST", "/api/v1/logout")
        except RestError:
            pass                      # cerrar sesion no debe romper el programa
        finally:
            self.token = None
            self.session.headers.pop("Authorization", None)

    # ─── El unico lugar que habla HTTP ────────────────────────────────
    def _request(self, metodo: str, ruta: str, autenticar: bool = True,
                 ok: tuple[int, ...] = (200, 201, 204), **kwargs) -> dict:
        """Ejecuta la peticion y traduce los errores HTTP a RestError."""
        if autenticar and not self.token:
            raise RestError(0, "No hay sesion: llamar a login() primero", metodo, ruta)

        url = f"{self.base_url}{ruta}"
        try:
            r = self.session.request(metodo, url, timeout=self.timeout, **kwargs)
        except requests.exceptions.SSLError as e:
            raise RestError(0, f"Error TLS: {e}", metodo, url) from e
        except requests.exceptions.ConnectTimeout as e:
            raise RestError(0, f"Timeout de conexion: {e}", metodo, url) from e
        except requests.exceptions.ConnectionError as e:
            raise RestError(0, f"No se pudo conectar: {e}", metodo, url) from e

        if r.status_code not in ok:
            raise RestError(r.status_code, self._detalle(r), metodo, url)
        if r.status_code == 204 or not r.content:
            return {}
        return r.json()

    @staticmethod
    def _detalle(r: requests.Response) -> str:
        """Extrae el mensaje de error del cuerpo, sea cual sea su forma.

        Cada vendor devuelve los errores con una estructura distinta. Esta
        funcion es el equivalente de check_config_errors() del cap. 10, y es
        mucho mas corta porque los codigos de estado hacen el trabajo pesado.
        """
        try:
            cuerpo = r.json()
        except ValueError:
            return r.text[:200] or r.reason

        for clave in ("detail", "message", "error", "errors"):
            if clave not in cuerpo:
                continue
            valor = cuerpo[clave]
            # Validadores tipo Pydantic/OpenAPI devuelven una lista de errores
            if isinstance(valor, list):
                return "; ".join(
                    f"{'.'.join(str(p) for p in e.get('loc', []))}: {e.get('msg', e)}"
                    if isinstance(e, dict) else str(e)
                    for e in valor
                )
            return str(valor)
        return str(cuerpo)[:200]

    # ─── Consultas (equivalente de los show) ──────────────────────────
    def get_system(self) -> dict:
        return self._request("GET", "/api/v1/system")

    def get_vlans(self) -> dict[int, str]:
        """Devuelve {vlan_id: nombre}. Ya viene estructurado: no hay que parsear."""
        datos = self._request("GET", "/api/v1/vlans")
        return {v["vlan_id"]: v["name"] for v in datos["vlans"]}

    def get_interfaces(self) -> dict[str, dict]:
        datos = self._request("GET", "/api/v1/interfaces")
        return {i.pop("name"): i for i in datos["interfaces"]}

    # ─── Cambios (equivalente de los config) ──────────────────────────
    def create_vlan(self, vlan_id: int, nombre: str) -> dict:
        """Crea la VLAN. Acepta 409 como exito: ya existia (idempotencia)."""
        return self._request("POST", "/api/v1/vlans",
                             json={"vlan_id": vlan_id, "name": nombre},
                             ok=(201, 409))

    def rename_vlan(self, vlan_id: int, nombre: str) -> dict:
        return self._request("PUT", f"/api/v1/vlans/{vlan_id}",
                             json={"name": nombre})

    def delete_vlan(self, vlan_id: int) -> dict:
        """Borra la VLAN. Acepta 404 como exito: ya no estaba."""
        return self._request("DELETE", f"/api/v1/vlans/{vlan_id}", ok=(204, 404))

    def patch_interface(self, nombre: str, **campos) -> dict:
        return self._request("PATCH", f"/api/v1/interfaces/{nombre}", json=campos)

    # ─── RESTCONF ─────────────────────────────────────────────────────
    def restconf_get(self, ruta_yang: str) -> dict:
        return self._request("GET", f"/restconf/data/{ruta_yang}",
                             headers={"Accept": "application/yang-data+json"})
