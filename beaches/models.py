from django.db import models
import uuid
from django.contrib.auth.models import User

#* ===== USER PROFILE & AUTH MODELS ===== *#
class UserProfile(models.Model):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nickname = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    lat = models.CharField(null=True, blank=True, default=48.8566)
    lng = models.CharField(null=True, blank=True, default=2.3522)
    
    xp = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username
    
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
    
    #MISC
    has_toilets = models.BooleanField(default=False)
    has_changing_rooms = models.BooleanField(default=False)
    
    # LUXURIES
    has_paid_zone = models.BooleanField(default=False)
    has_beach_bar = models.BooleanField(default=False)
    
    def __str__(self):
        return (F"{self.name}: {self.latitude},{self.longitude}")
    
class BeachImage(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(null=False, blank=False, upload_to='static/beach_images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        ('Хладно', 'cool'),
        ('Студено', 'cold'),
    )
    CROWD_LEVEL_CHOICES = (
        ('Високо', 'high'),
        ('Средно', 'meduim'),
        ('Ниско', 'low'),
    )
    WATER_CLARITY_CHOICES = (
        ('Облачна', 'cloudy'),
        ('Мътна', 'murky'),
        ('Ясна', 'clear'),
    )
    
    
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(BeachImage, on_delete=models.SET_NULL, blank=True, null=True)
    
    # conditions
    crowd_level = models.CharField(
        max_length=20,
        choices=CROWD_LEVEL_CHOICES,
        default='meduim',
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
    submitted_by = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    category = models.CharField(choices=REPORT_CATEGORIES, max_length=21)
    resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return (f"Report \"{self.title}\", made by {self.submitted_by.username} on {self.date}.")
    
class Badge(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField()
    desc = models.TextField()
    def __str__(self):
        return self.title