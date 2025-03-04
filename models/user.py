from config.config import base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    dni = Column(String(8), nullable=False, unique=True)
    
    
    
    
    __str__ = lambda self: f"User(id={self.id}, name={self.name}, email={self.email}, dni={self.dni})"
    
