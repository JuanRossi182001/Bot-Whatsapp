from fastapi import FastAPI
from routers import appointment,schedule,doctor,user
import prueba2
import prueba3
app = FastAPI()
app.include_router(appointment.router, prefix="/appointments", tags=["appointments"])
app.include_router(schedule.router, prefix="/schedules", tags=["schedules"])
app.include_router(doctor.router, prefix="/doctors", tags=["doctors"])
app.include_router(user.router, prefix="/users", tags=["users"])
# app.include_router(prueba2.router, prefix="/bot", tags=["bot"])
app.include_router(prueba3.router, prefix="/bot", tags=["bot"])


@app.get("/")
async def root():
    return {"message": "Hello World"}