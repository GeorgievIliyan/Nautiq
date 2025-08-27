from django.db import models
from django.contrib.auth.models import User

#* ===== USER PROFILE & AUTH MODELS ===== *#
class UserProfile(models.Model):
    nickname = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
    
#* ===== APP MODELS ===== *#
class BeachLocation(models.Model):
    latitude = models.FloatField()
    longtitude = models.FloatField()
    def __str__(self):
        return (f"{self.longtitude} {self.latitude}")
    
class Beach(models.Model):
    name = models.CharField(max_length=50)
    location = models.ForeignKey(BeachLocation, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return (F"{self.name}: {self.location}")
    
class BeachLog(models.Model):
    WATER_CLARITY_CHOICES = (
        ('clear','Ясна'),
        ('murky','Мътна'),
        ('cloudy','Облачна'),
    )
    CROWD_LEVEL_CHOICES = (
        ('low','Ниско'),
        ('meduim','Средно'),
        ('high','Високо')
    )
    WEATHER_CONDITION_CHOICES = (
        ('cold','Студено'),
        ('cool','Хладно'),
        ('normal','Нормално'),
        ('warm','Топло'),
        ('hot','Горещо')
    )
    WATER_TEMPERATURE_CHOICES = (
        ('cold','Студена'),
        ('cool','Хладна'),
        ('normal','Нормална'),
        ('warm','Топла'),
        ('hot','Гореща')
    )
    ALGAE_VOLUME_CHOICES = (
        ('none', 'Няма'),
        ('low', 'Малко'),
        ('medium', 'Средно'),
        ('high', 'Много'),
    )
    KIDS_AMOUNT_CHOICES = (
        ('none', 'Няма'),
        ('low', 'Малко'),
        ('medium', 'Средно'),
        ('high', 'Много'),
    )
    PARKING_SPACE_CHOICES = (
        ('none', 'Няма'),
        ('low', 'Малко'),
        ('medium', 'Средно'),
        ('high', 'Много'),
    )
    WAVE_CHOICES = (
        ('small', 'Малки'),
        ('medium', 'Средни'),
        ('high', 'Големи'),
    )
    
    
    beach = models.ForeignKey(Beach, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True)
    
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
    
    note = models.TextField(max_length=300, blank=True)
    
    # SAFETY
    has_lifegard = models.BooleanField(default=False)
    
    # PARKING & CAR RELATED
    has_parking = models.BooleanField(default=False)
    has_paid_parking = models.BooleanField(default=False)
    parking_space = models.CharField(
        max_length=20,
        choices=PARKING_SPACE_CHOICES,
        default='low',
        blank=True
    )
    
    #MISC
    has_toitlets = models.BooleanField(default=False)
    has_changing_rooms = models.BooleanField(default=False)
    
    # LUXURIES
    has_paid_zone = models.BooleanField(default=False)
    has_beach_bar = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Log for {self.beach.name} on {self.date.strftime('%Y-%m-%d')} by {self.user.username}"
    
    class Meta:
        ordering = ['-date']