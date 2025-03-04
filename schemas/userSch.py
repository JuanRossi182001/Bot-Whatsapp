from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated

class UserSch(BaseModel):
    name: str
    email: str
    dni: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=8,
            pattern=r"^\d+$",  # Asegura que solo contenga dígitos
        ),
    ]
    
    class Config:
        from_attributes = True
        
        
class UserResp(BaseModel):
    id: Optional[int]
    name: str
    email: str
    dni: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=8,
            pattern=r"^\d+$",  # Asegura que solo contenga dígitos
        ),
    ]
    
    class Config:
        from_attributes = True
        
        
        
class RequestUser(UserSch):
    pass 