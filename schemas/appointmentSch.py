from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentSch(BaseModel):
    user_id: int
    date: datetime
    doctor_id: int
    reason: Optional[str]
    
    class Config:
        from_attributes = True
        
        
class AppointmentResp(BaseModel):
    id: Optional[int]
    user_id: int
    doctor_id: int
    date: datetime
    reason: Optional[str]
    
    class Config:
        from_attributes = True
        
        
class RequestAppointment(AppointmentSch):
    pass