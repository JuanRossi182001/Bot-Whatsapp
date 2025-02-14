from typing import Annotated,List
from sqlalchemy.orm import Session
from config.db.connection import get_db
from fastapi import Depends
from schemas.doctorSch import DoctorResp,DoctorSch
from models.doctor import Doctor
from service.crud import CRUDService

class DoctorService(CRUDService[Doctor, DoctorSch, DoctorResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]) -> None:
        super().__init__(model=Doctor, response_schema=DoctorResp,db=db)
        
        


