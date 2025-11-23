from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

try:
    from beaches.models import UserProfile
except ImportError:
    UserProfile = None
    print("WARNING: UserProfile model not found. User profiles will not be created.")


User = get_user_model()

VARNA_LOCATION = {'lat': 43.2046, 'lng': 27.9106}
BURGAS_LOCATION = {'lat': 42.5048, 'lng': 27.4626}

# Admin User
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'AdminUser')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'AdminDefault1234')

# Test User 1 (Varna)
TEST1_USERNAME = os.getenv('TEST1_USERNAME', 'TestUser1')
TEST1_EMAIL = os.getenv('TEST1_EMAIL', 'testone@example.com')
TEST1_PASSWORD = os.getenv('TEST1_PASSWORD', 'TestDefault1234')

# Test User 2 (Burgas)
TEST2_USERNAME = os.getenv('TEST2_USERNAME', 'TestUser2')
TEST2_EMAIL = os.getenv('TEST2_EMAIL', 'testtwo@example.com')
TEST2_PASSWORD = os.getenv('TEST2_PASSWORD', 'TestDefault5678')


TEST_USERS_DATA = [
    {'username': TEST1_USERNAME, 'email': TEST1_EMAIL, 'password': TEST1_PASSWORD, 'location': VARNA_LOCATION},
    {'username': TEST2_USERNAME, 'email': TEST2_EMAIL, 'password': TEST2_PASSWORD, 'location': BURGAS_LOCATION},
]

ADMIN_USER_DATA = {
    'username': ADMIN_USERNAME, 
    'email': ADMIN_EMAIL, 
    'password': ADMIN_PASSWORD 
}


class Command(BaseCommand):
    help = 'Creates required test users, their profiles, and an admin superuser.'

    def handle(self, *args, **options):
        if not UserProfile:
            self.stdout.write(self.style.ERROR("ABORTED: Cannot create UserProfiles because the UserProfile model could not be imported."))
            return

        for user_data in TEST_USERS_DATA:
            username = user_data['username']
            
            if not User.objects.filter(username=username).exists():
                
                if 'Default' in user_data['password']:
                    self.stdout.write(self.style.WARNING(f"WARNING: User {username} created with default password."))
                
                user_instance = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password']
                )
                self.stdout.write(self.style.SUCCESS(f"Successfully created standard user: {username}"))

                UserProfile.objects.create(
                    user=user_instance,
                    nickname=username,
                    lat=str(user_data['location']['lat']),
                    lng=str(user_data['location']['lng'])
                )
                self.stdout.write(f"  -> Created UserProfile for {username}, centered on {user_data['location']['lat']}/{user_data['location']['lng']} (saved to lat/lng fields).")

            else:
                self.stdout.write(f"Standard user {username} already exists.")

        admin_data = ADMIN_USER_DATA
        admin_username = admin_data['username']
        
        if not User.objects.filter(username=admin_username).exists():
            
            if 'Default' in admin_data['password']:
                self.stdout.write(self.style.ERROR(f"ERROR: Admin user created with default password."))

            User.objects.create_superuser(
                username=admin_username,
                email=admin_data['email'],
                password=admin_data['password']
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully created admin superuser: {admin_username} (NO UserProfile created)."))
        else:
            self.stdout.write(f"Admin user {admin_username} already exists.")