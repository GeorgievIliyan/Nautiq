from . import models
import random
from datetime import date
from .models import Task

def check_badges(profile):
    unlocked = []

    if profile.missions_completed >= 10:
        unlocked.append('Explorer')
    if profile.xp >= 1000:
        unlocked.append('Achiever')

    for title in unlocked:
        badge = models.Badge.objects.filter(title=title).first()
        if badge and not profile.badge_set.filter(id=badge.id).exists():
            profile.badge_set.add(badge)
            
def generate_daily_tasks():
    print("🌀 Running daily task generator...")

    TASK_POOL = [
        ("Take a photo of a wave", "Go to the shore and capture a wave."),
        ("Collect 3 plastic bottles", "Clean up your area by picking up 3 bottles."),
        ("Spot a seagull", "Find and photograph a seagull."),
        ("Help a tourist", "Assist someone who’s lost or needs help."),
        ("Find driftwood", "Take a photo of an interesting piece of driftwood."),
        ("Recycle correctly", "Take a picture of your sorted recyclables."),
        ("Sunrise photo", "Capture the sunrise at the beach."),
        ("Sunset photo", "Capture the sunset at the beach."),
        ("Draw a map of your area", "Sketch or take a picture of your local coast."),
        ("Share a smile", "Take a picture of someone smiling near the water."),
    ]

    Task.objects.filter(is_daily=True).delete()

    daily_tasks = []
    for i in range(5):
        title, description = random.choice(TASK_POOL)
        daily_tasks.append(
            Task.objects.create(
                title=title,
                description=description,
                difficulty=random.choice(["easy", "medium", "hard"]),
                date_assigned=date.today(),
                is_daily=True,
            )
        )

    users = models.UserProfile.objects.all()
    for user in users:
        for task in daily_tasks:
            user.tasks.add(task)

    print(f"✅ {len(daily_tasks)} new daily tasks created and assigned to {len(users)} users.")
    return daily_tasks