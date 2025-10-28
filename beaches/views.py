import json
from datetime import date
import os

# Django imports
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.db.models import Count
from django.conf import settings
from django.template.loader import render_to_string

# Third-party imports
from validators.numbers_validator import is_valid_number as has_number
from validators.uppercase_validator import is_valid_uppercase as has_uppercase

# Local imports
from . import forms
from . import models

today_dt = timezone.localdate()
aware_datetime = timezone.now()

def is_moderator(user):
    return user.is_staff

def is_first_login(user):
    if user.is_first_login== True:
        return True
    else: False
    
def redirect_view(request):
    return redirect('dashboard')

User = get_user_model()

#* ===== MAILS ===== *#

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
            
            #* Validation & Checks
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
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                user.is_active = False
                user.save()

                #* Token building
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                #* Confirmation link
                confirmation_link = request.build_absolute_uri(
                    reverse('activate', kwargs={'uidb64': uid, 'token': token})
                )
                
                html_content = render_to_string('emails/confirm_account.html', {'username': username, 'confirmation_link': confirmation_link})

                send_mail(
                    subject= 'Потвърдете вашия акаунт в SeaSight',
                    html_message=html_content,
                    message=f'Здравей {username},\n\nМоля, потвърдете акаунта си като натиснете линка:\n{confirmation_link}\n\nБлагодарим! \nПоздрави: Екипа на SeaSight',
                    recipient_list=[email],
                    from_email= settings.DEFAULT_FROM_EMAIL,
                    fail_silently=False,
                )

                messages.success(request, "Регистрацията беше успешна! Моля, проверете имейла си, за да потвърдите акаунта.")
                return redirect('login')

            except Exception as user_register_error:
                messages.error(request, "Не успяхме да създадем акаунт! Моля, опитайте отново.")
                print(f"Error while registering user account: {user_register_error}")
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

            if models.UserProfile.objects.filter(nickname=nickname).exists():
                messages.error(request, "Този прякор е зает! Моля, използвайте друг.")
                return render(request, 'auth/register.html', {'form': form})

            try:
                models.UserProfile.objects.create(
                    user=user,
                    nickname=nickname,
                    lat=lat,
                    lng=lng
                )

                user.is_first_login = False
                user.save()

                return redirect("dashboard")

            except Exception as e:
                messages.error(request, f"Възникна грешка: {str(e)}")
                return render(request, 'auth/register.html', {'form': form})
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
    app_user = request.user
    context = {
        "user": app_user,
        "profile": models.UserProfile.objects.filter(user = app_user)
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

#* ================= APP ================= *#
@login_required
def dashboard(request):
    user = request.user
    
    if user.is_first_login:
        return redirect('enter_details')
    return render(request, 'app/dashboard.html', {'user': user})

@login_required
def map_view(request):
    jawg_token = settings.JAWG_ACCESS_TOKEN
    user = request.user
    user_profile = models.UserProfile.objects.filter(user=user).first()

    if user_profile:
        user_lat = user_profile.lat
        user_lng = user_profile.lng
    else:
        user_lat = 48.8566
        user_lng = 2.3522

    beaches = models.Beach.objects.filter(has_been_approved=True)

    beach_add_form = forms.BeachAddForm()
    beach_log_form = forms.LogBeachForm()
    beach_report_form = forms.ReportBeachForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "add_beach":
            print("Add progress!")
            beach_add_form = forms.BeachAddForm(request.POST, request.FILES)
            if beach_add_form.is_valid():
                added_beach = models.Beach.objects.create(
                    name=beach_add_form.cleaned_data['name'],
                    description=beach_add_form.cleaned_data['description'],
                    has_lifeguard=beach_add_form.cleaned_data['has_lifeguard'],
                    has_parking=beach_add_form.cleaned_data['has_parking'],
                    has_paid_parking=beach_add_form.cleaned_data['has_paid_parking'],
                    has_toilets=beach_add_form.cleaned_data['has_toilets'],
                    has_changing_rooms=beach_add_form.cleaned_data['has_changing_rooms'],
                    has_paid_zone=beach_add_form.cleaned_data['has_paid_zone'],
                    has_beach_bar=beach_add_form.cleaned_data['has_beach_bar'],
                    latitude=beach_add_form.cleaned_data['latitude'],
                    longitude=beach_add_form.cleaned_data['longitude'],
                )
                models.BeachImage.objects.create(
                    beach=added_beach,
                    title=added_beach.name,
                    user=user,
                    image=beach_add_form.cleaned_data['image']
                )
                messages.success(
                    request,
                    "Добавихте плаж успешно. Изчаква одобрение от администратор."
                )
                return redirect("map")
            else:
                print('mazna, ne ti raboti forma')
                print(beach_add_form.errors)

        elif form_type == "log_beach":
            print("Log progress")
            beach_log_form = forms.LogBeachForm(request.POST, request.FILES)
            if beach_log_form.is_valid():
                beach_id = request.POST.get("beach_id")
                beach = get_object_or_404(models.Beach, id=beach_id)
                image_file = beach_log_form.cleaned_data.get('image')

                if image_file:
                    beach_image_instance = models.BeachImage.objects.create(
                        beach=beach,
                        user=user,
                        title=image_file.name,
                        image=image_file
                    )
                else:
                    beach_image_instance = None

                models.BeachLog.objects.create(
                    beach=beach,
                    user=user,
                    image=beach_image_instance,
                    crowd_level=beach_log_form.cleaned_data['crowd_level'],
                    water_clarity=beach_log_form.cleaned_data['water_clarity'],
                    water_temp=beach_log_form.cleaned_data['water_temp'],
                    weather=beach_log_form.cleaned_data['weather'],
                    algae=beach_log_form.cleaned_data['algae'],
                    parking_space=beach_log_form.cleaned_data['parking_space'],
                    waves=beach_log_form.cleaned_data['waves'],
                    note=beach_log_form.cleaned_data['note']
                )
                profile = models.UserProfile.objects.get(user=user)
                profile.xp += 100
                profile.save()
                messages.info(request, '+100 XP точки!')
                return redirect("map")
            else:
                print('mazna ne ti raboti form-a')
                print(beach_log_form.errors)

    context = {
        "beaches": list(beaches.values("id", "latitude", "longitude")),
        "user_lat": user_lat,
        "user_lng": user_lng,
        "jawg_token": jawg_token,
        "beach_add_form": beach_add_form,
        "beach_log_form": beach_log_form,
        "beach_report_form": beach_report_form
    }

    return render(request, "app/map.html", context)

def beach_data(request, beach_id):
    today_dt = date.today()
    beach = models.Beach.objects.get(id=beach_id)
    
    today_logs = models.BeachLog.objects.filter(beach=beach, date__date=today_dt)
    logs_count = today_logs.count()

    response = {
        "pk": str(beach.pk),
        "log_id": str(today_logs.first().pk) if logs_count else None,
        "name": beach.name,
        "description": beach.description,
        "has_lifeguard": beach.has_lifeguard,
        "has_parking": beach.has_parking,
        "has_paid_parking": beach.has_paid_parking,
        "has_paid_zone": beach.has_paid_zone,
        "has_beach_bar": beach.has_beach_bar,
        "has_toilets": beach.has_toilets,
        "has_changing_rooms": beach.has_changing_rooms,
        "times_logged": logs_count,
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
            response[key] = most_common[field] if most_common else "Няма информация"

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
    return redirect('dashboard')

def terms(request):
    return render(request, 'terms.html')

@login_required
def app_settings(request):
    user = request.user

    try:
        user_profile = models.UserProfile.objects.get(user=user)
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

    return render(request, 'settings.html', {'form': form})

@login_required
def add_favourite(request, beach_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401) 

    user = request.user
    beach = get_object_or_404(models.Beach, id=beach_id)
    beach.favourites.add(user)
    
    return HttpResponse(status=204)