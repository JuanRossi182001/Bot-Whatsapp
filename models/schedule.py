from config.config import base
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship

class Schedule(base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer,ForeignKey("doctors.id"),nullable=False)
    day = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    
    
    __str__ = lambda self: f"Schedule(id={self.id}, doctor_id={self.doctor_id}, day={self.day}, start_time={self.start_time}, end_time={self.end_time})"