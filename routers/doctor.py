from fastapi import APIRouter, Depends,HTTPException,status
from service.doctor import DoctorService
from typing import Annotated
from sqlalchemy.exc import NoResultFound
from schemas.doctorSch import DoctorSch

router = APIRouter()

dependency = Annotated[DoctorService, Depends()]

# get all doctors
@router.get("/")
def get(service: dependency):
    return service.get_all()


# get doctor by id
@router.get("/{doctor_id}")
def get_by_id(doctor_id: int, service: dependency):
    try:
        return service.get_by_id(id=doctor_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# create doctor
@router.post("/create")
def create_doctor(doctor: DoctorSch, service: dependency):
    _doctor = service.create(obj_in=doctor)
    return _doctor


# delete doctor
@router.delete("/delete/{doctor_id}")
def delete(doctor_id: int, service: dependency):
    try:
        return service.delete(id=doctor_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# update doctor
@router.put("/update/{doctor_id}")
def update(doctor_id: int, doctor: DoctorSch, service: dependency):
    try:
        return service.update(id=doctor_id, obj_in=doctor)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))