class InMemoryDB:
    def __init__(self):
        # Empty local lists - No mock records loaded initially.
        # Active session data only.
        self.usuarios_db = []
        self.accesos_db = []

    def get_user(self, matricula: str):
        for u in self.usuarios_db:
            if u["matricula"] == matricula:
                return u
        return None

    def post_usuario(self, usuario_payload: dict) -> bool:
        if self.get_user(usuario_payload["matricula"]):
            return False
        self.usuarios_db.append(usuario_payload)
        return True

    def put_usuario(self, matricula: str, usuario_payload: dict) -> bool:
        for i, u in enumerate(self.usuarios_db):
            if u["matricula"] == matricula:
                self.usuarios_db[i] = usuario_payload
                return True
        return False

    def add_acceso(self, acceso_payload: dict):
        self.accesos_db.append(acceso_payload)

# Singleton database instance
db = InMemoryDB()
