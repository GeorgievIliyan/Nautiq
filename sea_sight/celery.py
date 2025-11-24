import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sea_sight.settings")

app = Celery("sea_sight")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "assign-daily-tasks": {
        "task": "beaches.tasks.assign_daily_tasks",
        "schedule": crontab(hour=0, minute=0),
    },
}