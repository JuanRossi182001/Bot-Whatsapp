import redis
import json

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host="localhost",  # Docker expone Redis en localhost:6379
            port=6379,
            decode_responses=True,  # Convierte bytes a strings
            password=None  
        )

    def save_session(self, from_number: str, session_data: dict, ttl: int = 86400):
        """Guarda la sesión en Redis con TTL (tiempo de expiración en segundos)."""
        key = f"session:{from_number}"
        self.client.execute_command("JSON.SET", key, "$", json.dumps(session_data))  # Guarda el JSON
        self.client.expire(key, ttl)  # Aplica el tiempo de expiración

    def get_session(self, from_number: str) -> dict:
        """Obtiene la sesión desde Redis."""
        key = f"session:{from_number}"
        session_json = self.client.execute_command("JSON.GET", key)  # Obtiene el JSON
        return json.loads(session_json) if session_json else {}  # Devuelve el JSON o un diccionario vacío
    
    
    
    def save_occupied_slot(self, doctor_id: int, date: str, slot: str, ttl: int = 86400):
        """
        Guarda un slot ocupado en Redis.
        :param doctor_id: ID del doctor.
        :param date: Fecha en formato 'YYYY-MM-DD'.
        :param slot: Slot ocupado en formato 'HH:MM-HH:MM'.
        :param ttl: Tiempo de expiración en segundos (por defecto 24 horas).
        """
        key = f"appointments:{doctor_id}:{date}"
        self.client.sadd(key, slot)  # Agrega el slot al conjunto
        self.client.expire(key, ttl)  # Establece el TTL para la clave

    def get_occupied_slots(self, doctor_id: int, date: str) -> set:
        """
        Obtiene los slots ocupados para un doctor y una fecha específicos.
        :param doctor_id: ID del doctor.
        :param date: Fecha en formato 'YYYY-MM-DD'.
        :return: Conjunto de slots ocupados.
        """
        key = f"appointments:{doctor_id}:{date}"
        return self.client.smembers(key)  # Devuelve un conjunto de slots ocupados

    def remove_occupied_slot(self, doctor_id: int, date: str, slot: str):
        """
        Elimina un slot ocupado de Redis.
        :param doctor_id: ID del doctor.
        :param date: Fecha en formato 'YYYY-MM-DD'.
        :param slot: Slot ocupado en formato 'HH:MM-HH:MM'.
        """
        key = f"appointments:{doctor_id}:{date}"
        self.client.srem(key, slot)  # Elimina el slot del conjunto

    def clear_occupied_slots(self, doctor_id: int, date: str):
        """
        Elimina todos los slots ocupados para un doctor y una fecha específicos.
        :param doctor_id: ID del doctor.
        :param date: Fecha en formato 'YYYY-MM-DD'.
        """
        key = f"appointments:{doctor_id}:{date}"
        self.client.delete(key)  # Elimina la clave y todos sus valores

# Instancia global para usar en tu aplicación
redis_client = RedisClient()