from pydantic import BaseModel,EmailStr
from typing import Optional

class AdminSch(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True
        
        
        
class AdminResp(BaseModel):
    id: Optional[int]
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True
        
        
        
class RequestAdmin(AdminSch):
    pass    
    