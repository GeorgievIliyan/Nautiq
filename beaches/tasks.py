from celery import shared_task
from .utils import generate_daily_tasks

@shared_task
def generate_daily_tasks_task():
    """
    Celery task that directly calls generate_daily_tasks()
    """
    generate_daily_tasks()
    return "Daily tasks generated and assigned"