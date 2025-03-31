from typing import Optional, List, Dict
from models.stage import BotStage

class Session:
    def __init__(
        self,
        user_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        dni: Optional[str] = None,
        stage: Optional[BotStage] = None,
        schedules: Optional[List[Dict]] = None,
        selected_schedule: Optional[Dict] = None,
        selected_appointment_id: Optional[int] = None,
        slots: Optional[List[str]] = None,
        selected_slot: Optional[str] = None,
        appointments: Optional[List[Dict]] = None,
        reason: Optional[str] = None
    ):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.name = name
        self.email = email
        self.dni = dni
        self.stage = stage or BotStage.GREET # Valor por defecto
        self.schedules = schedules
        self.selected_appointment_id = selected_appointment_id
        self.selected_schedule = selected_schedule
        self.slots = slots
        self.selected_slot = selected_slot
        self.appointments = appointments
        self.reason = reason

    def to_dict(self) -> dict:
        """Convierte la sesión a un diccionario compatible con Redis."""
        return {
            "user_id": self.user_id,
            "doctor_id": self.doctor_id,
            "name": self.name,
            "email": self.email,
            "dni": self.dni,
            "stage": self.stage.value if self.stage else None,
            "schedules": self.schedules,
            "selected_schedule": self.selected_schedule,
            "selected_appointment_id": self.selected_appointment_id,
            "slots": self.slots,
            "selected_slot": self.selected_slot,
            "appointments": self.appointments,
            "reason": self.reason
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Crea una instancia de Session desde un diccionario."""
        return cls(
            user_id=data.get("user_id"),
            doctor_id=data.get("doctor_id"),
            name=data.get("name"),
            email=data.get("email"),
            dni=data.get("dni"),
            stage=BotStage(data["stage"]) if data.get("stage") else BotStage.GREET,  # Convertir string a Enum
            schedules=data.get("schedules"),
            selected_schedule=data.get("selected_schedule"),
            selected_appointment_id=data.get("selected_appointment_id"),
            slots=data.get("slots"),
            selected_slot=data.get("selected_slot"),
            appointments=data.get("appointments"),
            reason=data.get("reason")
        )