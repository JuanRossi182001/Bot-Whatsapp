from models.appointment import Appointment
from schemas.appointmentSch import AppointmentResp, AppointmentSch
from service.crud import CRUDService
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.param_functions import Depends
from config.db.connection import get_db
from models.schedule import Schedule
from datetime import datetime


class AppointmentService(CRUDService[Appointment, AppointmentSch, AppointmentResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]):	
        super().__init__(model=Appointment, response_schema=AppointmentResp,db=db)
        
        
        
    def is_appointment_overlapping(self,doctor_id: int, appointment_date: datetime):
         overlapping_appointment = self.db.query(Appointment).filter(
             Appointment.doctor_id == doctor_id,
             Appointment.date == appointment_date
         ).first()
         return overlapping_appointment is not None
     
     
    def is_within_schedule(self, doctor_id: int, appointment_date: datetime):
        day = appointment_date.strftime('%A')
        schedule = self.db.query(Schedule).filter(
            Schedule.doctor_id == doctor_id,
            Schedule.day == day
        ).first()
        
        if not schedule:
            return False
        
        start_time = schedule.start_time
        end_time = schedule.end_time
        return start_time <= appointment_date <= end_time