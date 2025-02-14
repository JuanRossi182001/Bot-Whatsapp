from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class WeekDay(str, Enum):
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"

class ScheduleSch(BaseModel):
    doctor_id: int
    day: WeekDay
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True  


class ScheduleResp(BaseModel):
    id: Optional[int]
    doctor_id: int
    day: str
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True  


class RequestSchedule(ScheduleSch):
    pass
