from typing import Annotated
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.db.connection import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.adminSch import AdminResp,AdminSch
from models.admin import Admin
from service.crud import CRUDService
from sqlalchemy.orm.exc import NoResultFound

load_dotenv('variables.env')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES  = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

bcryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="admin/login")

class AdminService(CRUDService[Admin, AdminSch, AdminResp]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]) -> None:
        super().__init__(model=Admin, response_schema=AdminResp,db=db)
        
        
    def create(self, admin: AdminSch) -> AdminResp:
        hashed_password = bcryptContext.hash(admin.password)
        _admin = Admin(
            name=admin.name,
            email=admin.email,
            password=hashed_password
        )
        self.db.add(_admin)
        self.db.commit()
        self.db.refresh(_admin)
        return AdminResp.model_validate(_admin)
    
    
    def update(self, id: int, admin: AdminSch) -> AdminResp:
        _admin = self.db.query(Admin).filter(Admin.id == id).first()
        if not _admin:
            raise NoResultFound(f"Admin with id {id} not found")
        
        if admin.password:
            admin.password = bcryptContext.hash(admin.password)
        
        for key, value in admin.model_dump().items():
            setattr(admin, key, value)
        
        self.db.commit()
        self.db.refresh(_admin)
        return AdminResp.model_validate(_admin)
    
    
    def auth_admin(self, username: str, password: str) -> AdminResp:
        admin = self.db.query(Admin).filter(Admin.name == username).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        if not bcryptContext.verify(password, admin.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials"
            )
        return AdminResp.model_validate(admin)

    def create_token(self, admin_id: int, username: str, email: str, expires_delta: timedelta) -> str:
        to_encode = {'sub': username, 'id': admin_id, 'email': email}
        expire = datetime.utcnow() + expires_delta
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

def get_current_admin(service: Annotated[AdminService, Depends()], token: Annotated[str, Depends(oauth_bearer)]) -> AdminResp:
    
    payload = jwt.decode(token, SECRET_KEY)
    admin_id = payload.get('id')
    
    admin = service.get_by_id(admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    return AdminResp.model_validate(admin)
    
    
        