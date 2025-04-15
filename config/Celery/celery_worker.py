from celery import Celery
from config.Celery.functions import run_delete_old_schedules


celery_app = Celery("whatsappbot")

celery_app.config_from_object("config.Celery.celeryconfig")  # Carga la config desde tu archivo
celery_app.autodiscover_tasks(["config.Celery.functions"])