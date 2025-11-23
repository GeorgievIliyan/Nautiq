import json
import os
import random
from datetime import date
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env | Зареждане на променливи от .env файл

# Django imports | Django импорти
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
    get_user_model
)
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import django.utils as utils
from django.templatetags.static import static

# Third-party imports | Външни библиотеки
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image
from validators.numbers_validator import is_valid_number as has_number
from validators.uppercase_validator import is_valid_uppercase as has_uppercase
from difflib import SequenceMatcher
import uuid

# Local imports | Локални импорти
from . import forms, models
from .utils import (
    check_badges,
    generate_daily_tasks as generate_tasks,
    assign_weather,
    assign_wind
)
from beaches.ai.clip_recognizer import get_clip_match

# Globals | Глобални променливи
today_dt = timezone.localdate()  # Current local date | Текуща локална дата
aware_datetime = timezone.now()  # Current aware datetime | Текущо осъзнато време
User = get_user_model()  # Custom user model | Потребителски модел

# Utility functions | Полезни функции
def is_moderator(user):
    return user.is_staff  # Check if user is staff | Проверка дали потребителят е модератор

def is_first_login(user):
    return user.is_first_login is True  # Check first login flag | Проверка за първо влизане

def format_k(value):
    """
    Format number to short form: 1000 -> 1k, 1500 -> 1.5k | Форматира число в кратък вид
    """
    try:
        num = int(value)
    except (ValueError, TypeError):
        return str(value)

    if num < 1000:
        return str(num)

    thousands = num / 1000.0
    formatted = "%.1f" % thousands
    if formatted.endswith(".0"):
        formatted = formatted[:-2]
    return formatted + 'k'

User = get_user_model()

#* ===== MISC ===== *#
def homepage(request):
    return render(request, 'index.html')
#* ===== USER AUTHENTICATION ===== *#

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Validation checks
            if not has_uppercase(password):
                messages.error(request, "Паролата трябва да съдържа поне 1 главна буква.")
                return render(request, 'auth/register.html', {'form': form})
            if not has_number(password):
                messages.error(request, "Паролата трябва да съдържа поне 1 цифра.")
                return render(request, 'auth/register.html', {'form': form})
            if User.objects.filter(username=username).exists():
                messages.error(request, "Това потребителско име е заето! Моля, използвайте друго.")
                return render(request, 'auth/register.html', {'form': form})
            if User.objects.filter(email=email).exists():
                messages.error(request, "Този емайл е вече в употреба! Моля, използвайте друг.")
                return render(request, 'auth/register.html', {'form': form})

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email
                    )
                    user.is_active = False
                    user.save()

                    profile = models.UserProfile.objects.create(
                        user=user,
                        nickname=None,
                        lat=None,
                        lng=None
                    )

                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    confirmation_link = request.build_absolute_uri(
                        reverse('activate', kwargs={'uidb64': uid, 'token': token})
                    )
                    html_content = render_to_string('emails/confirm_account.html', {
                        'username': username,
                        'confirmation_link': confirmation_link
                    })

                    send_mail(
                        subject='Потвърдете вашия акаунт в SeaSight',
                        html_message=html_content,
                        message=f'Здравей {username},\n\nМоля, потвърдете акаунта си като натиснете линка:\n{confirmation_link}\n\nБлагодарим! \nПоздрави: Екипа на SeaSight',
                        recipient_list=[email],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        fail_silently=False,
                    )

                messages.success(request, "Регистрацията беше успешна! Моля, проверете имейла си, за да потвърдите акаунта.")
                return redirect('login')

            except Exception as e:
                messages.error(request, "Не успяхме да създадем акаунт! Моля, опитайте отново.")
                print(f"Error while registering user account: {e}")
                return render(request, 'auth/register.html', {'form': form})
    else:
        form = forms.RegisterForm()  
    return render(request, 'auth/register.html', {'form': form})

@login_required
@user_passes_test(is_first_login)
def enter_details(request):
    user = request.user
    if request.method == "POST":
        form = forms.UserPreferencesForm(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data['nickname']
            lat = form.cleaned_data['lat']
            lng = form.cleaned_data['lng']

            if models.UserProfile.objects.filter(nickname=nickname).exclude(user=user).exists():
                messages.error(request, "Този прякор е зает! Моля, използвайте друг.")
                return render(request, 'auth/enter_details.html', {'form': form})

            try:
                profile, created = models.UserProfile.objects.update_or_create(
                    user=user,
                    defaults={'nickname': nickname, 'lat': lat, 'lng': lng}
                )

                user.is_first_login = False
                user.save()

                return redirect("dashboard")

            except Exception as e:
                messages.error(request, f"Възникна грешка: {str(e)}")
                return render(request, 'auth/enter_details.html', {'form': form})
    else:
        form = forms.UserPreferencesForm()

    return render(request, 'auth/enter_details.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == "POST":
        print('User details send succesfully!')
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = authenticate(request, username=email, password=password)
            except Exception as user_login_error:
                print(f"An error occurred while a user was trying to log in: {user_login_error}")
                messages.error(request, 'An error occurred. Please try again.')
                return render(request, 'auth/login.html', {'form': form})

            if user is None:
                messages.error(request, 'Възникна грешка! Моля опитайте отново.')
                print('error')
                return render(request, 'auth/login.html', {'form': form})
            elif not user.is_active:
                messages.error(request, f'Моля потвърдете своя профил на {email}, преди да продължите!')
                print('error')
                return render(request, 'auth/login.html', {'form': form})
            else:
                login(request, user)
                messages.success(request, "Успешно влизане в профила!")
                return redirect('dashboard')
    else:
        form = forms.LoginForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def account_view(request):
    user = request.user
    profile = models.UserProfile.objects.get(user=user)
    if profile.profile_picture:
        pfp_url = profile.profile_picture.url
    else:
        pfp_url = static("default.webp") 

    context = {
        "user": user,
        "profile": profile,
        "email": user.email,
        "username": user.username,
        "nickname": profile.nickname,
        "lat": profile.lat,
        "lng": profile.lng,
        "pfp": pfp_url,
        "level": profile.level,
        "xp": profile.xp,
        "compl": profile.tasks_completed,
        "logs": models.BeachLog.objects.filter(user = user).count,
        "notifs": "Включени" if profile.send_notifs else "Изключени"
    }
    return render(request, 'auth/account.html', context)

@login_required
def account_delete(request):
    user = request.user
    if request.method == "POST":
        user_model_reference = User.objects.filter(username = user.username)
        user_model_reference.delete()
        return redirect('register')
    return render(request, 'auth/account_delete.html')

def enter_mail(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                reverse("set_new_password_from_mail", kwargs={"uidb64": uid, "token": token})
            )
            
            html_content = render_to_string('emails/reset_password_mail.html', {'user_name': 'Alex'})

            try:
                send_mail(
                    subject = "Възстановяване на парола - SeaSight",
                    message = f"Здравей {user.username},\n\nМожете да промените паролата си през този линк:\n{reset_link}\n\nПоздрави,\nЕкипа на SeaSight",
                    from_email= settings.DEFAULT_FROM_EMAIL,
                    recipient_list= [user.email],
                    html_message=html_content, 
                    fail_silently=False,
                )
                messages.success(request, "Изпратихме ви имейл с линк за смяна на парола.")
                return redirect("login")
            except Exception as ResetPasswordMailError:
                print(f"An error occured while trying to send a reset password mail: {ResetPasswordMailError}")
                messages.error(request, "Възникна грешка! Моля, опитайте отново!")
                
        else:
            messages.error(request, "Няма потребител с този имейл.")

    return render(request, "auth/enter_mail.html")


def set_new_password_from_mail(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = forms.SetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                messages.success(request, "Вашата парола беше променена успешно!")
                return redirect("login")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return render(
                    request,
                    "auth/set_new_password.html",
                    {"form": form, "uidb64": uidb64, "token": token},
                )
        else:
            form = forms.SetPasswordForm()

        return render(
            request,
            "auth/set_new_password.html",
            {"form": form, "uidb64": uidb64, "token": token},
        )
    else:
        messages.error(request, "Невалиден или изтекъл линк!")
        return redirect("enter_mail")


@login_required
def reset_password(request):
    user = request.user

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        if not user.check_password(old_password):
            messages.error(request, "Невалидна стара парола!")
        elif old_password == new_password:
            messages.error(request, "Новата парола не може да съвпада със старата!")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Паролата Ви беше успешно променена!")
            return redirect("account")

    return render(request, "auth/reset_password.html")

#* Activation View:
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Вашият акаунт беше потвърден! Вече можете да влезете.")
        return redirect('login')
    else:
        messages.error(request, "Невалиден или изтекъл линк за потвърждение.")
        return redirect('register')
    
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        models.UserProfile.objects.get(user = user).delete()
        models.User.objects.get(user = user).delete()
    return redirect("login")

#* ================= APP ================= *#
@login_required
def dashboard(request):
    user = request.user
    profile = models.UserProfile.objects.get(user=user)

    current_month = date.today().replace(day=1)

    monthly_stats, created = models.MonthlyStats.objects.get_or_create(
        user=profile,
        month=current_month,
        defaults={'tasks_completed': 0, 'xp': 0}
    )

    previous_stats = models.MonthlyStats.objects.filter(
        user=profile
    ).exclude(month=current_month).order_by('-month').first()

    def build_change(prev, curr, field):
        if not prev:
            return {"percent": "+0%", "is_up": True}

        prev_val = getattr(prev, field)
        curr_val = getattr(curr, field)

        if prev_val == 0:
            return {"percent": "+0%", "is_up": curr_val > 0}

        diff = round(((curr_val - prev_val) / prev_val) * 100)
        is_up = diff >= 0
        percent_str = f"{'+' if diff >= 0 else ''}{diff}%"

        return {"percent": percent_str, "is_up": is_up}

    xp_change = build_change(previous_stats, monthly_stats, "xp")
    tasks_change = build_change(previous_stats, monthly_stats, "tasks_completed")

    leaderboard = models.MonthlyStats.objects.filter(month=current_month).order_by('-xp')[:10]

    leaderboard_data = []
    for idx, stats in enumerate(leaderboard, start=1):
        leaderboard_data.append({
            'place': f"#{idx}",
            'username': stats.user.user.username,
            'score': stats.xp,
            'tasks_completed': stats.tasks_completed,
            'is_current_user': stats.user == profile,
            'profile_img': (
                stats.user.profile_img_url
                if hasattr(stats.user, 'profile_img_url')
                else "https://tinyurl.com/bdz6jnxj"
            )
        })

    context = {
        'user': user,
        'profile': profile,
        'monthly_stats': monthly_stats,
        'leaderboard': leaderboard_data,
        'xp_change': xp_change,
        'tasks_change': tasks_change,
    }

    if user.is_first_login:
        return redirect('enter_details')

    return render(request, 'app/dashboard.html', context)

@login_required
def map_view(request):
    user = request.user
    jawg_token = settings.JAWG_ACCESS_TOKEN
    user_profile = models.UserProfile.objects.filter(user=user).first()
    user_lat = user_profile.lat if user_profile else None
    user_lng = user_profile.lng if user_profile else None

    beaches = models.Beach.objects.filter(has_been_approved=True)

    beach_add_form = forms.BeachAddForm()
    beach_log_form = forms.LogBeachForm()
    beach_report_form = forms.ReportBeachForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "add_beach":
            beach_add_form = forms.BeachAddForm(request.POST, request.FILES)

            if beach_add_form.is_valid():
                beach = None
                try:
                    beach = models.Beach.objects.create(
                        name=beach_add_form.cleaned_data["name"],
                        description=beach_add_form.cleaned_data["description"],
                        latitude=beach_add_form.cleaned_data["latitude"],
                        longitude=beach_add_form.cleaned_data["longitude"],
                        has_lifeguard=beach_add_form.cleaned_data["has_lifeguard"],
                        has_parking=beach_add_form.cleaned_data["has_parking"],
                        has_paid_parking=beach_add_form.cleaned_data["has_paid_parking"],
                        has_toilets=beach_add_form.cleaned_data["has_toilets"],
                        has_changing_rooms=beach_add_form.cleaned_data["has_changing_rooms"],
                        has_paid_zone=beach_add_form.cleaned_data["has_paid_zone"],
                        has_beach_bar=beach_add_form.cleaned_data["has_beach_bar"],
                    )
                    print(f"[DEBUG] Created Beach (pending image validation): {beach}")

                    image_file = beach_add_form.cleaned_data.get("image")

                    if image_file:
                        image_pil = Image.open(image_file).convert("RGB")
                        
                        prompts = ["beach or shoreline or coast"]
                        
                        best_prompt, confidence, scores = get_clip_match(image_pil, prompts)
                        print(f"[DEBUG] CLIP match confidence: {confidence}")

                        VERIFICATION_THRESHOLD = 0.5 
                        
                        if confidence < VERIFICATION_THRESHOLD:
                            messages.error(request, "Снимката не беше разпозната като плаж! Моля, качете ясна снимка на плажа.")
                            if beach:
                                beach.delete()
                            return redirect("map")
                        img = models.BeachImage.objects.create(
                            beach=beach,
                            user=user,
                            image=image_file
                        )
                        print(f"[DEBUG] Created BeachImage for beach {beach.id}: {img}")

                        messages.success(request, "Плажът е добавен успешно!", extra_tags="bg-success")
                        return redirect("map")

                    else:
                        messages.error(request, "Моля добавете снимка на плажа!")
                        if beach:
                            beach.delete()
                        return redirect("map")

                except Exception as e:
                    print(f"[ERROR] Adding beach failed: {e}")
                    if beach:
                        beach.delete()
                    messages.error(request, "Неуспешно добавяне на плаж!", extra_tags="bg-danger")
                    return redirect("map")
        
        elif form_type == "log_beach":
            beach_log_form = forms.LogBeachForm(request.POST, request.FILES)

            if beach_log_form.is_valid():
                beach_id_raw = request.POST.get("beach") 
                
                if not beach_id_raw:
                    print("[ERROR] No beach ID in POST")
                    messages.error(request, "Не е избран плаж!")
                    return redirect("map")

                beach_id = None
                try:
                    if len(beach_id_raw) == 36 and '-' in beach_id_raw:
                        beach_id = uuid.UUID(beach_id_raw)
                    else:
                        beach_id = int(beach_id_raw)
                except (ValueError, TypeError):
                    print(f"[ERROR] Invalid Beach ID format: {beach_id_raw}")
                    messages.error(request, "Невалиден плаж!")
                    return redirect("map")

                try:
                    beach = models.Beach.objects.get(id=beach_id) 
                    
                    image_file = beach_log_form.cleaned_data.get("image")
                    if not image_file:
                        messages.error(request, "Нужна е снимка за доклада!")
                        return redirect("map")

                    image_pil = Image.open(image_file).convert("RGB")
                    prompts = ["a photo of a beach", "a photo of the sea", "a photo of a coastline", "a picture of sand and water"]
                    
                    best_prompt, confidence, scores = get_clip_match(image_pil, prompts)
                    print(f"[DEBUG] Log CLIP match confidence: {confidence}")

                    VERIFICATION_THRESHOLD = 0.5
                    
                    if confidence < VERIFICATION_THRESHOLD:
                        messages.error(request, "Снимката за доклада не беше разпозната като плаж!")
                        return redirect("map")
                    log_image = models.BeachImage.objects.create(
                        beach=beach,
                        user=user,
                        image=image_file
                    )
                    print(f"[DEBUG] Created BeachImage for log: {log_image}")

                    log = models.BeachLog.objects.create(
                        beach=beach,
                        user=user,
                        image=log_image,
                        crowd_level=beach_log_form.cleaned_data["crowd_level"],
                        water_clarity=beach_log_form.cleaned_data["water_clarity"],
                        water_temp=beach_log_form.cleaned_data["water_temp"],
                        weather=beach_log_form.cleaned_data["weather"],
                        algae=beach_log_form.cleaned_data["algae"],
                        parking_space=beach_log_form.cleaned_data["parking_space"],
                        waves=beach_log_form.cleaned_data["waves"],
                        note=beach_log_form.cleaned_data["note"],
                    )
                    print(f"[DEBUG] Created BeachLog: {log}")

                    messages.success(request, "Докладът е добавен успешно!")
                    return redirect("map")

                except models.Beach.DoesNotExist:
                    print(f"[ERROR] Beach with id {beach_id} does not exist.")
                    messages.error(request, "Невалиден плаж!")

                except Exception as e:
                    import traceback
                    print(f"[ERROR] Logging beach failed: {e}")
                    traceback.print_exc()
                    messages.error(request, "Неуспешно добавяне на доклад!")

            else:
                print("[DEBUG] LogBeachForm errors:", beach_log_form.errors)
                messages.error(request, "Формата съдържа грешки! Моля, проверете полетата.")
        
        elif form_type == "report_beach":
            beach_report_form = forms.ReportBeachForm(request.POST)
            if beach_report_form.is_valid():
                beach_id = request.POST.get("beach_id")
                try:
                    beach = models.Beach.objects.get(id=beach_id)
                    report = models.BeachReport.objects.create(
                        beach=beach,
                        submitted_by=user,
                        title=beach_report_form.cleaned_data["title"],
                        description=beach_report_form.cleaned_data["description"],
                        category=beach_report_form.cleaned_data["category"]
                    )
                    print(f"[DEBUG] Created BeachReport: {report}")
                    messages.success(request, "Сигналът е подаден успешно!")
                    return redirect("map")
                
                except models.Beach.DoesNotExist:
                    print(f"[ERROR] Beach with id {beach_id} does not exist.")
                    messages.error(request, "Невалиден плаж!")
                
                except Exception as e:
                    print(f"[ERROR] Reporting beach failed: {e}")
                    messages.error(request, "Неуспешно подаване на сигнал!")

    context = {
        "beaches": list(beaches.values("id", "latitude", "longitude")),
        "user_lat": user_lat,
        "user_lng": user_lng,
        "jawg_token": jawg_token,
        "beach_add_form": beach_add_form,
        "beach_log_form": beach_log_form,
        "beach_report_form": beach_report_form,
    }

    return render(request, "app/map.html", context)

def beach_data(request, beach_id):
    try:
        beach = models.Beach.objects.get(pk=beach_id)
    except models.Beach.DoesNotExist:
        return JsonResponse({"error": "Плажът не е намерен."}, status=404)
    except Exception as e:
        print(f"[ERROR] Beach lookup failed for ID {beach_id}: {e}")
        return JsonResponse({"error": "Грешка при зареждане на плажа."}, status=500)
        
    today_dt = date.today()
    today_logs = models.BeachLog.objects.filter(beach=beach, date__date=today_dt)
    logs_count = today_logs.count()
    
    lat = beach.latitude
    lng = beach.longitude
    
    beach_img = None
    try:
        image_obj = models.BeachImage.objects.filter(beach=beach).first()
        if image_obj:
            beach_img = image_obj.image.url
        else:
            beach_img = "/static/images/default_beach_placeholder.jpg"
    except Exception as e:
        print(f"[WARNING] Could not retrieve beach image for {beach.name}: {e}")
        beach_img = "/static/images/default_beach_placeholder.jpg" # Safe default

    degrees = None
    weather_desc = None
    weather_icon = None
    wind_speed = None
    wind_dir_text = None
    wind_dir_icon = None
    
    if lat and lng:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retries))

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": ["temperature_2m", "weathercode", "windspeed_10m", "winddirection_10m"],
            "current_weather": True
        }

        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            cw = data.get("current_weather", {})

            degrees = cw.get("temperature")
            weather_code = cw.get("weathercode")
            wind_speed = cw.get("windspeed")
            wind_deg = cw.get("winddirection")

            weather_desc, weather_icon = assign_weather(weather_code) 
            
            if wind_deg is not None:
                wind_dir_text, wind_dir_icon = assign_wind(wind_deg)
            else:
                wind_dir_text, wind_dir_icon = "Няма информация", "bi-question-circle"

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Open-Meteo API error: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error in weather fetch: {e}")

    response = {
        "pk": str(beach.pk),
        "log_id": str(today_logs.first().pk) if logs_count else None,
        "lat_lng": f"{lat}, {lng}",
        "name": beach.name,
        "beach_image": beach_img,
        "description": beach.description,
        "rating": beach.rating,
        "has_lifeguard": beach.has_lifeguard,
        "has_parking": beach.has_parking,
        "has_paid_parking": beach.has_paid_parking,
        "has_paid_zone": beach.has_paid_zone,
        "has_beach_bar": beach.has_beach_bar,
        "has_toilets": beach.has_toilets,
        "has_changing_rooms": beach.has_changing_rooms,
        "times_logged": logs_count,
        "degrees": degrees,
        "weather_desc": weather_desc,
        "weather_icon": weather_icon,
        "wind": wind_speed,
        "wind_direction_text": wind_dir_text,
        "wind_direction_icon": wind_dir_icon
    }

    if logs_count:
        fields_map = {
            "crowd_level": "crowd_avr",
            "water_clarity": "clarity_avr",
            "water_temp": "water_temp_avr",
            "weather": "weather_avr",
            "algae": "algae_avr",
            "kids": "kids_avr", 
            "waves": "waves",
            "parking_space": "parking_space"
        }

        for field, key in fields_map.items():
            most_common = (
                today_logs
                .values(field)
                .annotate(count=Count(field))
                .order_by('-count')
                .first()
            )
            response[key] = most_common.get(field) if most_common else "Няма информация"

    return JsonResponse(response)

@login_required
def favourite_beaches(request):
    user = request.user
    favourite_beaches = models.Beach.objects.filter(favourites=user)
    
    return render(request, 'app/beaches/favourites.html', {'favourites': favourite_beaches})


#* ===== MODERATION ===== *#
@user_passes_test(is_moderator)
@login_required
def dashboard_mod(request):
    pending_beaches = models.Beach.objects.filter(has_been_approved=False).prefetch_related('beachimage_set')
    reports = models.BeachReport.objects.filter(resolved = False)
    context = {
        'pending': pending_beaches,
        'reports': reports
    }
    return render(request, 'app/moderator/dashboard_mod.html', context)

@user_passes_test(is_moderator)
@login_required
def mark_as_approved(request, beach_id):
    beach = get_object_or_404(models.Beach, id = beach_id)
    beach.has_been_approved = True
    beach.approved_date = timezone.now()
    beach.save()
    return redirect('dashboard_mod')
    
@user_passes_test(is_moderator)
@login_required
def delete_beach(request, beach_id):
    beach = get_object_or_404(models.Beach, id = beach_id)
    beach.delete()
    return redirect('dashboard_mod')
    
#* ====== BEACH REPORTING ===== *#
@login_required
def report_beach(request, beach_id):
    beach = get_object_or_404(models.Beach, id = beach_id)
    user = request.user
    if request.method == "POST":
        form = forms.ReportBeachForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            
            try:
                new_report = models.BeachReport.objects.create(
                    beach = beach,
                    submitted_by = user,
                    title = title,
                    description = description,
                    category = category
                )
                messages.success(request, 'Успешно подадено докладване!')
                
                subject = "Успешно подаден сигнал"
                message = f"Здравейте, {user.username}, \n\nБлагодарим, че подадохте сигнал за този плаж. Модерацията ще прегледа този сигнал възможно най-бързо.\nID на сигнала: {new_report.id}. \n\nПоздрави:\nEкипът на SeaSight"
                from_email = 'iliyan.georgiev09@gmail.com'
                recipent_list = [user.email]
                
                send_mail(subject, message, from_email, recipent_list)
                
                return redirect('map')
            except Exception as e:
                print(f"Error while trying to submit report: {e}")
                messages.error(request, 'Възникна грешка! Моля, опитайте отново.')
                return render(request, 'app/reports/report_add.html', {'form': form})
    else:
        form = forms.ReportBeachForm()
    
    return render(request, 'app/reports/report_add.html', {'form':form})

@login_required
@user_passes_test(is_moderator)
def report_mark_as_resolved(request, report_id):
    beach = get_object_or_404(models.BeachReport, id = report_id)
    beach.resolved = True
    beach.save()
    return redirect("moderation_dashboard")
    
def report_delete(request, report_id):
    beach = get_object_or_404(models.BeachReport, id = report_id)
    beach.delete()
    return redirect("moderation_dashboard")

#* ====== BEACH LOGGING ===== *#
@login_required
def view_logs_spec(request, beach_id):
    beach = get_object_or_404(models.Beach, pk=beach_id)

    logs = models.BeachLog.objects.filter(beach=beach, date=today_dt)

    return render(request, 'app/logs/logs_today.html', {
        'beach': beach,
        'logs': logs
    })

@login_required
def view_my_logs(request):
    user = request.user
    logs = models.BeachLog.objects.filter(user = user)
    context = {
        'logs': logs
    }
    return render(request, 'app/logs/my_logs.html', context)

#* ===== MISC VIEWS ===== *#
def redirect_from_empty_link(request):
    if is_moderator(request.user):
        return redirect('dashboard_mod')
    return redirect('dashboard')

def terms(request):
    return render(request, 'terms.html')

@login_required
def app_settings(request):
    try:
        user_profile = models.UserProfile.objects.get(user=request.user)
    except models.UserProfile.DoesNotExist:
        messages.error(request, 'Профилът ви не беше намерен.')
        return redirect('home')

    if request.method == 'POST':
        form = forms.SettingsForm(request.POST)
        if form.is_valid():
            user_profile.theme = form.cleaned_data['theme']
            user_profile.send_notifs = form.cleaned_data['notifs']
            user_profile.language = form.cleaned_data['lang']

            try:
                user_profile.save()
                messages.success(request, 'Настройките бяха успешно запазени!')
                return redirect('app_settings')
            except Exception:
                messages.error(request, 'Не успяхме да съхраним вашите настройки! Моля, опитайте отново.')
        else:
            messages.error(request, 'Възникна грешка във формата! Проверете въведените данни.')
    else:
        form = forms.SettingsForm(initial={
            'theme': user_profile.theme,
            'notifs': user_profile.send_notifs,
            'lang': user_profile.language,
        })
        settings = {
            'theme': user_profile.theme,
            'notifs': user_profile.send_notifs,
            'lang': user_profile.language
        }

    return render(request, 'app/settings.html', {'form': form, 'settings': settings})

@login_required
def add_favourite(request, beach_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401) 

    user = request.user
    beach = get_object_or_404(models.Beach, id=beach_id)
    beach.favourites.add(user)
    
    return HttpResponse(status=204)

#* ===== GAMIFICATION ===== *#
@receiver(signal=post_save, sender=models.AcceptedTask)
def handle_task_completion(sender, instance, created, **kwargs):
    if instance.status == 'completed' and instance.completed_at:
        profile = instance.user_profile
        task = instance.task

        profile.xp += task.reward
        profile.tasks_completed += 1
        profile.save()

        today = timezone.now().date()
        first_of_month = today.replace(day=1)
        stats, _ = models.MonthlyStats.objects.get_or_create(user=profile, month=first_of_month)
        stats.xp += task.reward
        stats.tasks_completed += 1
        stats.save()

        check_badges(profile)

@login_required
def complete_task(request, task_id):
    print(f"[DEBUG] Start complete_task for task_id={task_id}")

    if request.method != 'POST':
        print("[DEBUG] Method not POST")
        messages.error(request, "Възникна грешка! Очаква се POST заявка.")
        return redirect('tasks')

    try:
        profile = models.UserProfile.objects.get(user=request.user)
        print(f"[DEBUG] Found user profile: {profile}")
    except models.UserProfile.DoesNotExist:
        print("[DEBUG] UserProfile does not exist")
        messages.error(request, "Не успяхме да открием профил! Моля, опитайте отново!")
        return redirect('tasks')

    accepted_task = get_object_or_404(
        models.AcceptedTask,
        user_profile=profile,
        task_id=task_id,
        status='accepted'
    )
    print(f"[DEBUG] Accepted task found: {accepted_task}")

    image = request.FILES.get('proof_image')
    if not image:
        print("[DEBUG] No image uploaded")
        messages.error(request, "Нужна е снимка за потвърждение!")
        return redirect('tasks')

    filename = f"{accepted_task.id}_proof_image_{image.name}"
    saved_path = default_storage.save(os.path.join('proof_images', filename), image)
    file_path = default_storage.path(saved_path)
    print(f"[DEBUG] Image saved to: {file_path}")

    if not os.path.exists(file_path):
        print("[DEBUG] File does not exist on disk!")
        return HttpResponse(f"Грешка: Файлът не съществува на {file_path}", status=500)

    task_description = accepted_task.task.description or ""
    print(f"[DEBUG] Task description: {task_description}")

    try:
        best_match, confidence, scores = get_clip_match(file_path, [task_description])
        print(f"[DEBUG] CLIP results -> best_match: {best_match}, confidence: {confidence}, scores: {scores}")
    except Exception as e:
        print(f"[DEBUG] Error in get_clip_match: {e}")
        best_match = ""
        confidence = 0.0
        scores = []

    try:
        confidence_float = float(confidence)
    except (ValueError, TypeError):
        print(f"[DEBUG] Invalid confidence value: {confidence}")
        confidence_float = 0.0
    
    VERIFICATION_THRESHOLD = 0.5 

    verified = confidence_float > VERIFICATION_THRESHOLD
    print(f"[DEBUG] Verified: {verified} (Confidence: {confidence_float} vs Threshold: {VERIFICATION_THRESHOLD})")
    
    accepted_task.proof_image = saved_path
    accepted_task.verified = verified
    accepted_task.verification_confidence = confidence_float

    if verified:
        accepted_task.status = 'completed'
        accepted_task.completed_at = timezone.now()
        accepted_task.save()
        print("[DEBUG] Task marked as completed")

        difficulty_xp = {'easy': 20, 'medium': 50, 'hard': 100}
        reward_xp = difficulty_xp.get(accepted_task.task.difficulty, 10)
        profile.xp += reward_xp
        profile.save()

        try:
            check_badges(profile)
        except Exception as e:
            print(f"[DEBUG] Badge check failed: {e}")

        messages.success(request, f"Ура! Успешно изпълнена задача! Спечелихте {reward_xp} XP.")
        return redirect('tasks')
    
    else:
        accepted_task.status = 'accepted'
        accepted_task.save()
        print("[DEBUG] Task verification FAILED")
        messages.error(
            request,
            "Снимката не съвпада с описанието на задачата! Уверете се, че снимката е ясна и опитайте отново."
        )

    print("[DEBUG] complete_task finished")
    return redirect('tasks')

@login_required
def accept_task(request, task_id):
    if request.method != "POST":
        return HttpResponse("Method not allowed.", status=405)

    profile = models.UserProfile.objects.filter(user = request.user).get()
    task = get_object_or_404(models.Task, id=task_id)

    already_taken = models.AcceptedTask.objects.filter(
        user_profile=profile, task=task
    ).exists()

    if already_taken:
        return messages.error(request, "Вече сте приели тази задача!")

    models.AcceptedTask.objects.create(
        user_profile=profile,
        task=task,
        status="accepted",
        accepted_at=timezone.now(),
    )

    return redirect("tasks")

@login_required
def tasks_view(request):
    profile = models.UserProfile.objects.get(user=request.user)

    all_tasks = models.Task.objects.all()

    accepted_tasks = models.AcceptedTask.objects.filter(
        user_profile=profile, status='accepted'
    )
    completed_tasks = models.AcceptedTask.objects.filter(
        user_profile=profile, status='completed'
    )

    xp_to_next_level = profile.xp_for_next_level - profile.xp

    context = {
        "tasks": all_tasks,
        "accepted_ids": list(accepted_tasks.values_list("task_id", flat=True)),
        "completed_ids": list(completed_tasks.values_list("task_id", flat=True)),
        "xp_to_next_level": xp_to_next_level,
        "current_xp": profile.xp,
        "current_level": profile.level,
        "xp_next": profile.xp_for_next_level,
    }

    return render(request, "app/gamification/tasks.html", context)