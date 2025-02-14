from config.config import base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Doctor(base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    specialty = Column(String(50), nullable=True)
    
    
    
    __str__ = lambda self: f"Doctor(id={self.id}, name={self.name}, specialty={self.specialty})"