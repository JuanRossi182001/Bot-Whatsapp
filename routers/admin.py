from fastapi import APIRouter
from service.admin import AdminService
from schemas.adminSch import AdminSch
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from models.token import Token
from datetime import timedelta
router = APIRouter()

dependency = Annotated[AdminService, Depends()]

# get all admins
@router.get("/")
def get(service: dependency):
    _admins = service.get_all()
    return _admins

# get by id
@router.get("/{admin_id}")
def get_by_id(admin_id: int, service: dependency):
    try:
        _admin = service.get_by_id(id=admin_id)
        return _admin
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# create admin
@router.post("/create")
def create(admin: AdminSch, service: dependency):
    _admin = service.create(admin=admin)
    return _admin
    
    
# update admin
@router.patch("/update/{admin_id}")
def update(admin_id: int, admin: AdminSch, service: dependency):
    try:
        _admin = service.update(id=admin_id, obj_in=admin)
        return _admin
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# delete admin
@router.delete("/delete/{admin_id}")
def delete(admin_id: int, service: dependency):
    try:
        return service.delete(id=admin_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# login for acces token 
@router.post("/login", response_model=Token)
def login_for_token(service: dependency,form_data: OAuth2PasswordRequestForm = Depends()):
    _admin = service.auth_admin(username=form_data.username, password=form_data.password)
    if not _admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    access_token = service.create_token(admin_id=_admin.id, username=_admin.name, email=_admin.email, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}