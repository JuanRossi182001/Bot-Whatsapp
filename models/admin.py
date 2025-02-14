from config.config import base
from sqlalchemy import Integer,Column,String



class Admin(base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    
    
   