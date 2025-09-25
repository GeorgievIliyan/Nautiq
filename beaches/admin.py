from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Beach, BeachLog, BeachReport

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_first_login',)}),
    )
    
    # Also, update the 'add_fieldsets' for the 'Add User' page
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_first_login',)}),
    )

@admin.register(User)
class UserAdmin(CustomUserAdmin):
    pass

admin.site.register(UserProfile)
admin.site.register(Beach)
admin.site.register(BeachLog)
admin.site.register(BeachReport)