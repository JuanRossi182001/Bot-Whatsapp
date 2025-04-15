from typing import Annotated,List
from sqlalchemy.orm import Session
from config.db.connection import get_db
from fastapi import Depends,HTTPException,status
from schemas.scheduleSch import ScheduleResp,ScheduleSch
from models.schedule import Schedule
from service.crud import CRUDService
from sqlalchemy.exc import NoResultFound
from datetime import datetime



class ScheduleService(CRUDService[Schedule, ScheduleSch, ScheduleResp]):
    def __init__(self, db: Annotated[Session,Depends(get_db)]):
        super().__init__(model=Schedule, response_schema=ScheduleResp,db=db)


    def get_by_doctor(self, doctor_id: int) -> List[ScheduleResp]:
        try:
            _schedules = self.db.query(Schedule).filter(Schedule.doctor_id == doctor_id).all()
            
            if not _schedules:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedules not found")
            
            return [ScheduleResp.model_validate(schedule) for schedule in _schedules]
        except NoResultFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    
    def delete_old_schedules(self):
        today = datetime.now()
        self.db.query(Schedule).filter(Schedule.start_time < today).delete()
        self.db.commit()
        print(f"Deleted schedules older than {today}")
        
    
            
        
