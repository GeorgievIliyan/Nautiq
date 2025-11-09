from django.core.management.base import BaseCommand
from datetime import date
from beaches.models import Task, UserProfile
import random

class Command(BaseCommand):
    help = "Assigns new daily tasks to all users."

    def handle(self, *args, **options):
        today = date.today()
        for profile in UserProfile.objects.all():
            difficulties = ['easy', 'medium', 'hard']
            for diff in difficulties:
                available = Task.objects.filter(difficulty=diff, date_assigned__isnull=True)
                if available.exists():
                    task = random.choice(list(available))
                    task.date_assigned = today
                    task.save()
                    profile.tasks.add(task)

        self.stdout.write(self.style.SUCCESS("✅ Daily tasks assigned successfully!"))