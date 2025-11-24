from celery import shared_task
from django.core.management import call_command

@shared_task
def assign_daily_tasks():
    call_command("assign_daily_tasks")