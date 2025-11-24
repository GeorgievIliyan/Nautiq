from django.core.management.base import BaseCommand
from beaches.utils import generate_daily_tasks

class Command(BaseCommand):
    help = "Generates the global daily tasks and assigns them to users."

    def handle(self, *args, **options):
        generate_daily_tasks()
        self.stdout.write(self.style.SUCCESS("Daily tasks generated and assigned."))