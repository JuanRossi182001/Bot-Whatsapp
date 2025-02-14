from typing import Optional, List, Dict

class Session:
    def __init__(
        self,
        user_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        stage: Optional[str] = None,
        schedules: Optional[List[Dict]] = None,
        selected_schedule: Optional[Dict] = None,
        slots: Optional[List[str]] = None,
        selected_slot: Optional[str] = None
    ):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.name = name
        self.email = email
        self.stage = stage or "greet"  # Valor por defecto
        self.schedules = schedules
        self.selected_schedule = selected_schedule
        self.slots = slots
        self.selected_slot = selected_slot

    def to_dict(self) -> dict:
        """Convierte la sesión a un diccionario compatible con Redis."""
        return {
            "user_id": self.user_id,
            "doctor_id": self.doctor_id,
            "name": self.name,
            "email": self.email,
            "stage": self.stage,
            "schedules": self.schedules,
            "selected_schedule": self.selected_schedule,
            "slots": self.slots,
            "selected_slot": self.selected_slot
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Crea una instancia de Session desde un diccionario."""
        return cls(
            user_id=data.get("user_id"),
            doctor_id=data.get("doctor_id"),
            name=data.get("name"),
            email=data.get("email"),
            stage=data.get("stage"),
            schedules=data.get("schedules"),
            selected_schedule=data.get("selected_schedule"),
            slots=data.get("slots"),
            selected_slot=data.get("selected_slot")
        )