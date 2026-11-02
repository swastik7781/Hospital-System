from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "hospital_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.notifications"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "send-daily-appointment-reminders": {
            "task": "app.tasks.notifications.send_appointment_reminders_task",
            "schedule": crontab(hour=7, minute=0),  # Run every morning at 7 AM
        },
        "check-low-stock-medicines": {
            "task": "app.tasks.notifications.check_low_stock_task",
            "schedule": crontab(hour=8, minute=0),  # Run every morning at 8 AM
        },
    },
)
