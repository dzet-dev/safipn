import requests
import os
from .config import DEFAULT_API_URL

# Maps for converting IDs to human-readable strings (mirroring the backend catalogs)
PUERTA_MAP = {1: "Puerta 1 AV. Té", 2: "Puerta 2 Resina", 3: "Puerta 3 Sur 187", 4: "Puerta 4 Canela"}
PROG_MAP = {
    1: "Lic. en Administración Industrial",
    2: "Ingeniería en Informática",
    3: "Ingeniería en Transporte",
    4: "Ingeniería Ferroviaria",
    5: "Ingeniería Industrial",
    6: "Lic. en Ciencias de la Informática"
}


class SAFIPNApiClient:
    def __init__(self, base_url=DEFAULT_API_URL):
        self.base_url = base_url

    def get_url(self, endpoint):
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    # ── Health ─────────────────────────────────────────────────────

    def check_health(self) -> bool:
        try:
            response = requests.get(self.get_url("/"), timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    # ── Accesos ────────────────────────────────────────────────────

    def verificar_acceso(self, puerta_id: int, tipo_mov: int, foto_path: str):
        """POST /acceso/verificar/ — envía foto y datos de acceso."""
        url = self.get_url("/acceso/verificar/")
        data = {"puerta_id": puerta_id, "tipo_mov": tipo_mov}

        if not os.path.exists(foto_path):
            return False, "Archivo de foto no encontrado para verificación."
        try:
            with open(foto_path, 'rb') as f:
                files = {'file': ('rostro_acceso.jpg', f, 'image/jpeg')}
                response = requests.post(url, data=data, files=files, timeout=15)
            if response.status_code == 200:
                return True, response.json()
            detail = "Error desconocido"
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                pass
            return False, f"Código {response.status_code}: {detail}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def registrar_visitante(self, motivo: str, puerta_id: int, tipo_mov: int):
        """POST /acceso/visitante/ — registra visitante sin biometría."""
        url = self.get_url("/acceso/visitante/")
        payload = {"motivo": motivo, "puerta_id": puerta_id, "tipo_mov": tipo_mov}
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code in [200, 201]:
                return True, response.json()
            return False, f"Error del servidor: Código {response.status_code}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def listar_accesos(self, puerta_id: int = None, estatus_acce: int = None, limit: int = 300):
        """GET /acceso/ — obtiene el historial completo de accesos."""
        url = self.get_url("/acceso/")
        params = {"limit": limit}
        if puerta_id is not None:
            params["puerta_id"] = puerta_id
        if estatus_acce is not None:
            params["estatus_acce"] = estatus_acce
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return True, response.json()
            return False, f"Código {response.status_code}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    # ── Usuarios ───────────────────────────────────────────────────

    def registrar_usuario(self, usuario_payload: dict, foto_path: str):
        """POST /usuarios/ — crea usuario con biometría (multipart/form-data)."""
        url = self.get_url("/usuarios/")
        if not os.path.exists(foto_path):
            return False, "Archivo de foto no encontrado para registrar usuario."
        try:
            with open(foto_path, 'rb') as f:
                files = {'file': ('rostro_registro.jpg', f, 'image/jpeg')}
                response = requests.post(url, data=usuario_payload, files=files, timeout=15)
            if response.status_code in [200, 201]:
                return True, response.json()
            detail = "Error desconocido"
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                pass
            return False, f"Código {response.status_code}: {detail}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def listar_usuarios(self):
        """GET /usuarios/ — lista todos los usuarios."""
        url = self.get_url("/usuarios/")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True, response.json()
            return False, f"Código {response.status_code}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def update_usuario(self, id_usuario: int, update_payload: dict):
        """PUT /usuarios/{id_usuario}."""
        url = self.get_url(f"/usuarios/{id_usuario}")
        try:
            response = requests.put(url, json=update_payload, timeout=5)
            if response.status_code == 200:
                return True, response.json()
            return False, f"Código {response.status_code}: {response.text}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def eliminar_usuario(self, id_usuario: int):
        """DELETE /usuarios/{id_usuario} — eliminado lógico (vigencia=0)."""
        url = self.get_url(f"/usuarios/{id_usuario}")
        try:
            response = requests.delete(url, timeout=5)
            if response.status_code == 204:
                return True, "Usuario desactivado correctamente."
            return False, f"Código {response.status_code}: {response.text}"
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"


# Singleton client
api_client = SAFIPNApiClient()
