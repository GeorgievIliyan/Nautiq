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

    ICON_MAP = {
        "Вълна": "bi-water",
        "Мида": "bi-egg-fried",
        "Рапан": "bi-egg-fried",
        "Морска пяна": "bi-droplet",
        "Облак": "bi-cloud",
        "Морска трева": "bi-tree",
        "Чист пясък": "bi-brush",
        "Пластмасова бутилка": "bi-bottle",
        "Капачка": "bi-circle",
        "Дърво": "bi-tree",
        "Следи в пясъка": "bi-footprint",
        "Камък": "bi-square",
        "Черупка от мида": "bi-egg",
        "Линията на прилива": "bi-water",
        "Плажен отпадък": "bi-trash",
        "Тъмен облак": "bi-clouds",
        "Светъл облак": "bi-cloud-sun",
        "Водорасли": "bi-tree",
        "Голяма водораслова купчина": "bi-tree-fill",
        "Пясъчна формация": "bi-square",
        "Камък с форма": "bi-circle",
        "Морски предмет от дърво": "bi-tree",
        "Слънце и вода": "bi-sun",
        "Фар": "bi-lighthouse",
        "Кей или пристан": "bi-box-seam",
        "Отдалечен плаж": "bi-geo-alt",
        "Голяма вълна": "bi-water",
        "Скална формация": "bi-geo",
        "Морска пещера": "bi-geo-alt-fill",
    }

    TASK_POOL = [
        ("Вълна", "Отиди до брега и заснеми морска вълна.", "wave", "easy"),
        ("Мида", "Намери мида на плажа и я заснеми.", "shell", "easy"),
        ("Рапан", "Открий рапан и направи снимка.", "rapana", "easy"),
        ("Морска пяна", "Заснеми зона с морска пяна.", "foam", "easy"),
        ("Облак", "Снимай облак над морето.", "cloud", "easy"),
        ("Голяма водораслова купчина", "Заснеми голяма купчина водорасли.", "seaweed pile", "medium"),
        ("Пясъчна формация", "Снимай интересна пясъчна формация.", "sand formation", "medium"),
        ("Камък с форма", "Намери камък с интересна форма.", "shaped stone", "medium"),
        ("Морски предмет от дърво", "Заснеми дървен предмет, изхвърлен от морето.", "driftwood", "medium"),
        ("Слънце и вода", "Снимай отражението на слънцето във водата.", "sun", "medium"),
        ("Фар", "Намери и заснеми фар или маяк.", "lighthouse", "hard"),
        ("Кей или пристан", "Снимай мост, кей или пристан.", "pier", "hard"),
        ("Отдалечен плаж", "Снимай изолиран плажен участък.", "beach", "hard"),
        ("Голяма вълна", "Снимай висока или разбиваща се вълна.", "wave", "hard"),
    ]

    models.Task.objects.filter(is_daily=True).delete()

    easy_tasks = [t for t in TASK_POOL if t[3] == "easy"]
    medium_tasks = [t for t in TASK_POOL if t[3] == "medium"]
    hard_tasks = [t for t in TASK_POOL if t[3] == "hard"]

    num_easy = int(8 * 0.6)   # 5
    num_medium = int(8 * 0.3) # 2
    num_hard = 8 - num_easy - num_medium # 1

    selected_tasks = random.sample(easy_tasks, num_easy) + \
                        random.sample(medium_tasks, num_medium) + \
                        random.sample(hard_tasks, num_hard)

    daily_tasks = []
    for title, user_desc, description, difficulty in selected_tasks:
        icon = ICON_MAP.get(title, "bi-star")
        task = models.Task.objects.create(
            title=title,
            user_desc=user_desc,
            description=description,
            difficulty=difficulty,
            date_assigned=date.today(),
            is_daily=True,
            icon=icon
        )
        daily_tasks.append(task)

    users = models.UserProfile.objects.all()
    for user in users:
        user.tasks.add(*daily_tasks)

    print(f"✅ {str(len(daily_tasks)) +  " x " + str(len(users))} new daily tasks created and assigned to {len(users)} users.")
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