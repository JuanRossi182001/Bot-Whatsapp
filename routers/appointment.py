from fastapi import APIRouter, Depends,HTTPException,status
from service.appointment import AppointmentService
from schemas.appointmentSch import AppointmentSch
from sqlalchemy.exc import NoResultFound
from typing import Annotated

router = APIRouter()

dependency = Annotated[AppointmentService, Depends()]

# get all appointments
@router.get("/")
def get(service: dependency):
    return service.get_all()


# get appointment by id
@router.get("/{appo_id}")
def get_by_id(appo_id: int, service: dependency):
    try:
        return service.get_by_id(id=appo_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# create appointment
@router.post("/create")
async def create_appointment(appointment: AppointmentSch, service: dependency):
    if service.is_appointment_overlapping(doctor_id=appointment.doctor_id, appointment_date=appointment.date):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The doctor already has an appointment at that time.")
    
    if not service.is_within_schedule(doctor_id=appointment.doctor_id, appointment_date=appointment.date):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The doctor is not available at that time.")
    
    
    _appointment = service.create(obj_in=appointment)
    return _appointment
    
    
# delete appointment
@router.delete("/delete/{appo_id}")
def delete_appointment(appo_id: int, service: dependency):
    try:
        return service.delete(id=appo_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
# update appointment
@router.put("/update/{appo_id}")
def update_appointment(appo_id: int, appointment: AppointmentSch, service: dependency):
    try:
        return service.update(id=appo_id, obj_in=appointment)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    

@router.get("/id/{user_id}")
def get_by_user_id(user_id: int, service: dependency):
    try:
        return service.get_by_user_id(user_id=user_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
@router.get("/doctor_id/{doctor_id}")
def get_by_user_id(doctor_id: int, service: dependency):
    try:
        return service.get_by_doctor_id(doctor_id=doctor_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) 
    