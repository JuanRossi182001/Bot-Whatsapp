from celery.schedules import crontab

beat_schedule = {
    "delete-old-schedules-daily": {
        "task": "config.Celery.functions.run_delete_old_schedules",  # Ruta completa del task
        "schedule": crontab(hour=0, minute=0),  # Ejecutar todos los días a las 00:00
    },
}

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

timezone = "America/Argentina/Buenos_Aires"
enable_utc = False

