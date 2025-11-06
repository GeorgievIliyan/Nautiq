import math

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# from .utils import get_clip_match

import uuid

#* ===== USER PROFILE & AUTH MODELS ===== *#
class User(AbstractUser):
    is_first_login = models.BooleanField(default=True)

class UserProfile(models.Model):
    LANGUAGE_CHOICES = (
        ('bg', 'Български'),
        ('en', 'Английски')
    )
    # USER DATA
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # GEO LOCATION
    lat = models.CharField(null=True, blank=True, default=48.8566)
    lng = models.CharField(null=True, blank=True, default=2.3522)
    # XP
    xp = models.IntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)

    # SETTINGS
    theme = models.CharField(null=True, blank=True, default="light")
    send_notifs = models.BooleanField(null=True, blank=True, default=True)
    language = models.CharField(choices=LANGUAGE_CHOICES, default="bg")

    # GAMIFICATION
    @property
    def level(self):
        """Compute level from XP"""
        return int(0.1 * math.sqrt(self.xp))

    @property
    def xp_for_next_level(self):
        next_level = self.level + 1
        return int((next_level / 0.1) ** 2)

    @property
    def progress_percent(self):
        prev_level_xp = int((self.level / 0.1) ** 2)
        return round(((self.xp - prev_level_xp) / (self.xp_for_next_level - prev_level_xp)) * 100, 2)

    def __str__(self):
        return f"{self.user.username} with nickname {self.nickname}"
    
class MonthlyStats(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='monthly_stats')
    month = models.DateField()
    tasks_completed = models.PositiveIntegerField(default=0)
    xp = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'month')

#* ===== APP MODELS ===== *#
class Beach(models.Model):
    has_been_approved = models.BooleanField(default=False)
    approved_date = models.DateTimeField(null=True, blank=True)
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=250, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    #* SAFETY
    has_lifeguard = models.BooleanField(default=False)
    
    #* PARKING & CAR RELATED
    has_parking = models.BooleanField(default=False)
    has_paid_parking = models.BooleanField(default=False)
    
    #* MISC
    has_toilets = models.BooleanField(default=False)
    has_changing_rooms = models.BooleanField(default=False)
    
    #* LUXURIES
    has_paid_zone = models.BooleanField(default=False)
    has_beach_bar = models.BooleanField(default=False)
    
    #* FAVOURITES  
    favourites = models.ManyToManyField(User, related_name="favourite_beaches", blank=True)
    
    def __str__(self):
        return f"{self.name}: {self.latitude},{self.longitude}"

class BeachImage(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(null=False, blank=False, upload_to='static/beach_images/')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return (f"Image \"{self.title}\" created on {self.date} by {self.user.username}.")

class BeachLog(models.Model):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    WAVE_CHOICES = (
        ('Големи', 'high'),
        ('Средни', 'medium'),
        ('Малки', 'small'),
    )
    PARKING_SPACE_CHOICES = (
        ('Много', 'high'),
        ('Средно', 'medium'),
        ('Малко', 'low'),
        ('Няма', 'none'),
    )
    KIDS_AMOUNT_CHOICES = (
        ('Много', 'high'),
        ('Средно', 'medium'),
        ('Малко', 'low'),
        ('Няма', 'none'),
    )
    ALGAE_VOLUME_CHOICES = (
        ('Много', 'high'),
        ('Средно', 'medium'),
        ('Малко', 'low'),
        ('Няма', 'none'),
    )
    WATER_TEMPERATURE_CHOICES = (
        ('Гореща', 'hot'),
        ('Топла', 'warm'),
        ('Нормална', 'normal'),
        ('Хладна', 'cool'),
        ('Студена', 'cold'),
    )
    WEATHER_CONDITION_CHOICES = (
        ('Горещо', 'hot'),
        ('Топло', 'warm'),
        ('Нормално', 'normal'),
        ('Хладко', 'cool'),
        ('Студено', 'cold'),
    )
    CROWD_LEVEL_CHOICES = (
        ('Високо', 'high'),
        ('Средно', 'medium'),
        ('Ниско', 'low'),
    )
    WATER_CLARITY_CHOICES = (
        ('Облачна', 'cloudy'),
        ('Мътна', 'murky'),
        ('Ясна', 'clear'),
    )
    
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(BeachImage, on_delete=models.SET_NULL, blank=True, null=True)
    
    crowd_level = models.CharField(
        max_length=20,
        choices=CROWD_LEVEL_CHOICES,
        default='medium',
        blank=True
    )
    
    water_clarity = models.CharField(
        max_length=20,
        choices=WATER_CLARITY_CHOICES,
        default='clear',
        blank=True
    )
    
    water_temp = models.CharField(
        max_length=20,
        choices=WATER_TEMPERATURE_CHOICES,
        default='normal',
        blank=True
    )
    
    weather = models.CharField(
        max_length=20,
        choices=WEATHER_CONDITION_CHOICES,
        default='normal',
        blank=True
    )
    
    algae = models.CharField(
        max_length=20,
        choices=ALGAE_VOLUME_CHOICES,
        default='low',
        blank=True
    )
    
    kids = models.CharField(
        max_length=20,
        choices=KIDS_AMOUNT_CHOICES,
        default='low',
        blank=True
    )
    
    waves = models.CharField(
        max_length=20,
        choices=WAVE_CHOICES,
        default='low',
        blank=True
    )
    
    parking_space = models.CharField(
        max_length=20,
        choices=PARKING_SPACE_CHOICES,
        default='low',
        blank=True
    )
    
    note = models.TextField(max_length=300, blank=True)
    
    def __str__(self):
        return f"Log for {self.beach.name} on {self.date.strftime('%Y-%m-%d')} by {self.user.username}"
    
    class Meta:
        ordering = ['-date']

class BeachReport(models.Model):
    REPORT_CATEGORIES = (
        ('inc_loc', 'Неправилно местоположение'),
        ('inc_info', 'Неточна информация'),
        ('ins_cont', 'Обидна информация'),
        ('other', 'Друго'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    category = models.CharField(choices=REPORT_CATEGORIES, max_length=21)
    resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return (f"Report \"{self.title}\", made by {self.submitted_by.username} on {self.date}.")
    
#* ===== GAMIFICATION ===== *#
class Task(models.Model):
    
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=[('easy','Easy'),('medium','Medium'),('hard','Hard')], default='easy')
    reward = models.PositiveIntegerField(default=10)
    
    def __str__(self):
        return self.title


class Badge(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField()
    desc = models.TextField()
    
    def __str__(self):
        return self.title

class AcceptedTask(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('accepted', 'В прогрес'),
        ('completed', 'Завършено'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted')

    accepted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    proof_image = models.ImageField(upload_to='task_proofs/', blank=True, null=True)
    
    def analyze_image(self):
        prompts = ["a beach", "a soda can", "a plastic bottle", "trash", "sand", "sea"]
        # best, conf, _ = get_clip_match(self.image.path, prompts)
        # self.label = best
        # self.confidence = conf
        # self.save()

    class Meta:
        unique_together = ('user_profile', 'task')

    def __str__(self):
        return f"{self.user_profile.user.username}'s {self.task.title} task"

    def complete(self, image=None):
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        if image:
            self.proof_image = image
        self.save()