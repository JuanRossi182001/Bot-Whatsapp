from config.config import base
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship


class Appointment(base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)  
    date = Column(DateTime)
    reason = Column(String(50), nullable=True)
    
    
    

    
    __str__ = lambda self: f"Appointment(id={self.id}, user_id={self.user_id}, doctor_id={self.doctor_id}, date={self.date})"
    
    
