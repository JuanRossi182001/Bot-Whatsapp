from typing import Annotated,List
from sqlalchemy.orm import Session
from config.db.connection import get_db
from fastapi import Depends
from schemas.userSch import UserResp,UserSch
from models.user import User
from service.crud import CRUDService
class UserService(CRUDService[User, UserSch, UserResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]) -> None:
        super().__init__(model=User, response_schema=UserResp,db=db)
        
        
    def user_exist(self, email: str, dni: str) -> dict:
    # Buscar usuario por DNI
        user_by_dni = self.db.query(User).filter(User.dni == dni).first()
        
        # Buscar usuario por email
        user_by_email = self.db.query(User).filter(User.email == email).first()
        
        if user_by_dni and user_by_email and user_by_dni.id == user_by_email.id:
            # El DNI y el email están registrados y corresponden al mismo usuario
            return user_by_dni
        elif user_by_dni:
            # El DNI está registrado, pero el email no coincide
            return None
        else:
            # El DNI no está registrado
            return False
        
    