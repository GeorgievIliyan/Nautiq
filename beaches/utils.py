from . import models
import random
from datetime import date
from .models import Task
from collections import OrderedDict

def check_badges(profile):
    unlocked = []

    if profile.tasks_completed >= 10:
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

WEATHER_MAP = {
    0: ("Ясно", "bi-sun-fill"),
    1: ("Предимно ясно", "bi-sun"),
    2: ("Преобладаващо облачно", "bi-cloud-sun"),
    3: ("Облачно", "bi-cloud"),
    45: ("Мъгла", "bi-cloud-fog"),
    48: ("Мъгла с ледени кристали", "bi-cloud-fog"),
    51: ("Слаб дъжд (капки)", "bi-cloud-drizzle"),
    53: ("Умерен дъжд (капки)", "bi-cloud-drizzle"),
    55: ("Силен дъжд (капки)", "bi-cloud-drizzle"),
    56: ("Леден слаб дъжд", "bi-cloud-drizzle"),
    57: ("Леден силен дъжд", "bi-cloud-drizzle"),
    61: ("Слаб дъжд", "bi-cloud-rain"),
    63: ("Умерен дъжд", "bi-cloud-rain"),
    65: ("Силен дъжд", "bi-cloud-rain"),
    66: ("Слаб ледено студен дъжд", "bi-cloud-rain"),
    67: ("Силен ледено студен дъжд", "bi-cloud-rain"),
    71: ("Слаб сняг", "bi-snow"),
    73: ("Умерен сняг", "bi-snow"),
    75: ("Силен сняг", "bi-snow"),
    77: ("Сняг на ситни частици", "bi-snow"),
    80: ("Проливен дъжд", "bi-cloud-rain"),
    81: ("Силен проливен дъжд", "bi-cloud-rain"),
    82: ("Много силен проливен дъжд", "bi-cloud-rain"),
    85: ("Леко снеговалеж", "bi-snow"),
    86: ("Силен снеговалеж", "bi-snow"),
    95: ("Буря с гръмотевици", "bi-cloud-lightning"),
    96: ("Буря с гръмотевици и градушка", "bi-cloud-lightning"),
    99: ("Силна буря с градушка", "bi-cloud-lightning")
}

def assign_weather(weather_code):
    return WEATHER_MAP.get(weather_code, ("Няма информация", "bi-question-circle"))

def assign_wind(deg):
    directions = OrderedDict([
        (22.5, ("С", "bi-arrow-up")),
        (67.5, ("СИ", "bi-arrow-up-right")),
        (112.5, ("И", "bi-arrow-right")),
        (157.5, ("ЮИ", "bi-arrow-down-right")),
        (202.5, ("Ю", "bi-arrow-down")),
        (247.5, ("ЮЗ", "bi-arrow-down-left")),
        (292.5, ("З", "bi-arrow-left")),
        (337.5, ("СЗ", "bi-arrow-up-left")),
        (360, ("С", "bi-arrow-up")),
    ])
    for threshold, (dir_text, icon) in directions.items():
        if deg < threshold:
            return dir_text, icon
    return "С", "bi-arrow-up"