from pydantic import BaseModel
from typing import Optional

class DoctorSch(BaseModel):
    name: str
    specialty: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class DoctorResp(BaseModel):
    id: Optional[int]
    name: str
    specialty: Optional[str] = None
    
    class Config:
        from_attributes = True
        
        
        
class RequestDoctor(DoctorSch):
    pass 