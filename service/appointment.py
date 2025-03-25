from models.appointment import Appointment
from schemas.appointmentSch import AppointmentResp, AppointmentSch
from service.crud import CRUDService
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.param_functions import Depends
from config.db.connection import get_db
from models.schedule import Schedule
from datetime import datetime
from sqlalchemy.exc import NoResultFound


class AppointmentService(CRUDService[Appointment, AppointmentSch, AppointmentResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]):	
        super().__init__(model=Appointment, response_schema=AppointmentResp,db=db)
        
        
    def get_by_doctor_id(self, doctor_id: int):
        _appointments = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
        if not _appointments:
            raise NoResultFound(f"Appointment with doctor_id {doctor_id} not found")
        return [self.response_schema.model_validate(appointment) for appointment in _appointments]
        
    def get_by_user_id(self, user_id: int):
        _appointments = self.db.query(Appointment).filter(Appointment.user_id == user_id).all()
        if not _appointments:
            raise NoResultFound(f"Appointment with user_id {user_id} not found")
        return [self.response_schema.model_validate(appointment) for appointment in _appointments]
    
    def is_appointment_overlapping(self,doctor_id: int, appointment_date: datetime):
         overlapping_appointment = self.db.query(Appointment).filter(
             Appointment.doctor_id == doctor_id,
             Appointment.date == appointment_date
         ).first()
         return overlapping_appointment is not None
     
     
    def is_within_schedule(self, doctor_id: int, appointment_date: datetime):
        # 1. Obtener el día de la semana en el mismo formato que Schedule.day
        day = appointment_date.strftime('%A')  # Ejemplo: "Monday"
        
        # 2. Buscar el horario del doctor para ese día
        schedule = self.db.query(Schedule).filter(
            Schedule.doctor_id == doctor_id,
            Schedule.day == day
        ).first()
        
        if not schedule:
            return False  # No hay horario para ese día
        
        # 3. Convertir start_time y end_time al mismo día que appointment_date
        start_time = schedule.start_time.replace(
            year=appointment_date.year,
            month=appointment_date.month,
            day=appointment_date.day
        )
        end_time = schedule.end_time.replace(
            year=appointment_date.year,
            month=appointment_date.month,
            day=appointment_date.day
        )
        
        # 4. Comparar las fechas y horas
        return start_time <= appointment_date <= end_time