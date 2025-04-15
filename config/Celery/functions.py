from config.db.connection import get_db
from service.schedule import ScheduleService
from celery import shared_task


@shared_task
def run_delete_old_schedules():
    db = next(get_db())
    service = ScheduleService(db)
    service.delete_old_schedules()