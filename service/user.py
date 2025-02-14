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
        
        
    def user_exist(self, email: str, name: str) -> bool:
        if self.db.query(User).filter(email == User.email).filter(name == User.name).first():
            _user = self.db.query(User).filter(email == User.email).filter(name == User.name).first()
            return _user
        return False
        
    