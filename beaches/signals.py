from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.db.models import F
from .models import AcceptedTask, MonthlyStats

@receiver(post_save, sender=AcceptedTask)
def update_profile_and_stats(sender, instance, created, **kwargs):
    if instance.status != 'completed':
        return

    profile = instance.user_profile

    profile.xp += instance.task.reward
    profile.tasks_completed += 1
    profile.save()
    print(f"[Signal] Updated profile: XP={profile.xp}, tasks_completed={profile.tasks_completed}")

    today = now().date()
    month_start = today.replace(day=1)
    stats_qs = MonthlyStats.objects.filter(user=profile, month=month_start)
    if stats_qs.exists():
        stats_qs.update(tasks_completed=F('tasks_completed') + 1)
        print(f"[Signal] MonthlyStats updated for {profile.user.username}, month={month_start}")
    else:
        MonthlyStats.objects.create(user=profile, month=month_start, tasks_completed=1)
        print(f"[Signal] MonthlyStats created for {profile.user.username}, month={month_start}")