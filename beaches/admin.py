from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.UserProfile)
admin.site.register(models.Beach)
admin.site.register(models.BeachLog)
admin.site.register(models.BeachReport)