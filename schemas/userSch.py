from pydantic import BaseModel
from typing import Optional

class UserSch(BaseModel):
    name: str
    email: str
    
    class Config:
        from_attributes = True
        
        
class UserResp(BaseModel):
    id: Optional[int]
    name: str
    email: str
    
    class Config:
        from_attributes = True
        
        
        
class RequestUser(UserSch):
    pass 