from fastapi import FastAPI,Depends,HTTPException,status
from typing import Annotated
from models.admin import Admin
from routers import appointment,schedule,doctor,user,admin
import routers.prueba3 as prueba3
from service.admin import get_current_admin


app = FastAPI()
app.include_router(appointment.router, prefix="/appointments", tags=["appointments"])
app.include_router(schedule.router, prefix="/schedules", tags=["schedules"])
app.include_router(doctor.router, prefix="/doctors", tags=["doctors"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(prueba3.router, prefix="/bot", tags=["bot"])

# auth test
admin_dependency = Annotated[Admin,Depends(get_current_admin)]
@app.get("/")
async def root(admin: admin_dependency):
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    return {"message": "Hello World"}