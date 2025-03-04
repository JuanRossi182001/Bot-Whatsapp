from service.user import UserService
from schemas.userSch import UserSch
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.exc import NoResultFound
from typing import Annotated

router = APIRouter()

dependency = Annotated[UserService, Depends()]

# get all users
@router.get("/")
def get(service: dependency):
    return service.get_all()

# get user by id
@router.get("/{user_id}")
def get_by_id(user_id: int, service: dependency):
    try:
        return service.get_by_id(id=user_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
# create user
@router.post("/create")
def create_user(user: UserSch, service: dependency):
    
    existing_user = service.user_exist(email=user.email, dni=user.dni)
    
    if existing_user:
        return existing_user
    elif existing_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al registrar el usuario. El email no coincide con el Dni. Por favor, ingresa el Dni nuevamente.")
    else:
        _user = service.create(obj_in=user)
        return _user
        
    
    


# delete user
@router.delete("/delete/{user_id}")
def delete(user_id: int, service: dependency):
    try:
        return service.delete(id=user_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    

# update user
@router.put("/update/{user_id}")
def update(user_id: int, user: UserSch, service: dependency):
    try:
        return service.update(id=user_id, obj_in=user)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))