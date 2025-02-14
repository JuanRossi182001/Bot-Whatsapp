from service.schedule import ScheduleService,Depends
from fastapi import APIRouter,HTTPException,status
from sqlalchemy.exc import NoResultFound
from typing import Annotated
from schemas.scheduleSch import ScheduleSch
from sqlalchemy.exc import IntegrityError

router = APIRouter()

dependency = Annotated[ScheduleService, Depends()]

# get all schedules
@router.get("/")
def get(service: dependency):
    return service.get_all()

# get schedule by id
@router.get("/{schedule_id}")
def get_by_id(schedule_id: int, service: dependency):
    try:
        return service.get_by_id(id=schedule_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
    
# create schedule
@router.post("/create")
def create_schedule(schedule: ScheduleSch, service: dependency):
    try:
        _schedule = service.create(obj_in=schedule)
        return _schedule
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is not a doctor with that id.")


# delete schedule
@router.delete("/delete/{schedule_id}")    
def delete_schedule(schedule_id: int, service: dependency):
    try:
        return service.delete(id=schedule_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
    
# update schedule
@router.put("/update/{schedule_id}")
def update_schedule(schedule_id: int, schedule: ScheduleSch, service: dependency):
    try:
        return service.update(id=schedule_id, obj_in=schedule)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
# get schedule by doctor id
@router.get("/doctor/{doctor_id}")
def get_by_doctor(doctor_id: int, service: dependency):
    try:
        return service.get_by_doctor(doctor_id=doctor_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
