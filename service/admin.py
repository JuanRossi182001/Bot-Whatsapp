from typing import Annotated,List
from sqlalchemy.orm import Session
from config.db.connection import get_db
from fastapi import Depends
from schemas.adminSch import AdminResp,AdminSch
from models.admin import Admin
from service.crud import CRUDService

class DoctorService(CRUDService[Admin, AdminSch, AdminResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]) -> None:
        super().__init__(model=Admin, response_schema=AdminResp,db=db)