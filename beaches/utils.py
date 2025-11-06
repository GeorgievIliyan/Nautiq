from . import models

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