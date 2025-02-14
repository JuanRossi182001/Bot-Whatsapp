import redis
import json

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host="localhost",  # Docker expone Redis en localhost:6379
            port=6379,
            decode_responses=True,  # Convierte bytes a strings
            password=None  # Si configuraste una contraseña en Redis, colócala aquí
        )

    def save_session(self, from_number: str, session_data: dict, ttl: int = 86400):
        """Guarda la sesión en Redis con TTL (tiempo de expiración en segundos)."""
        self.client.setex(
            f"session:{from_number}",
            ttl,
            json.dumps(session_data)  # Convierte el diccionario a JSON
        )

    def get_session(self, from_number: str) -> dict:
        """Obtiene la sesión desde Redis."""
        session_json = self.client.get(f"session:{from_number}")
        if session_json:
            return json.loads(session_json)
        return {}  # Devuelve un diccionario vacío si no existe la sesión

# Instancia global para usar en tu aplicación
redis_client = RedisClient()