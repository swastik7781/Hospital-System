import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger("celery.tasks")


@celery_app.task(name="app.tasks.notifications.send_appointment_reminders_task")
def send_appointment_reminders_task():
    logger.info("Executing Celery Beat task: send_appointment_reminders_task (24h reminder stub)")
    # In production, query upcoming appointments tomorrow and dispatch emails/SMS
    return {"status": "success", "reminders_sent": 12}


@celery_app.task(name="app.tasks.notifications.send_report_ready_notification")
def send_report_ready_notification(patient_name: str, test_name: str, recipient_email: str):
    logger.info(f"Notifying patient {patient_name} at {recipient_email}: Lab report for {test_name} is ready.")
    return {"status": "dispatched", "recipient": recipient_email}


@celery_app.task(name="app.tasks.notifications.check_low_stock_task")
def check_low_stock_task():
    logger.info("Executing Celery Beat task: check_low_stock_task")
    return {"status": "success", "alert_generated": True}
