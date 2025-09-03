import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sea_sight.settings")
django.setup()

from beaches.models import BeachReport

def delete_old_reports():
    cutoff = timezone.now() - timedelta(weeks=2)
    deleted_count, _ = BeachReport.objects.filter(resolved=True, date__lt=cutoff).delete()
    print(f"Deleted {deleted_count} old resolved reports")

if __name__ == "__main__":
    delete_old_reports()