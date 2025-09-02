from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.core.serializers import serialize
from validators.numbers_validator import is_valid_number as has_number
from validators.uppercase_validator import is_valid_uppercase as has_uppercase
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from . import models
import json
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils import timezone
from . import forms

def is_moderator(user):
    return user.is_staff

#* ===== USER AUTHENTICATION ===== *#

def register_view(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            nickname = form.cleaned_data['nickname']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            #* Validation & Checks
            if models.UserProfile.objects.filter(nickname = nickname).exists():
                messages.error(request, "Този прякор е зает! Моля, използвайте друг.")
                return render(request, 'auth/register.html', {'form': form})
            if has_uppercase(password) != True:
                messages.error(request, "Паролата трябва да съдържа поне 1 главна буква.")
                return render(request, 'auth/register.html', {'form': form})
            if has_number(password) != True:
                messages.error(request, "Паролата трябва да съдържа поне 1 цифра.")
                return render(request, 'auth/register.html', {'form': form})
            if User.objects.filter(username = username).exists():
                messages.error(request, "Това потребителско име е заето! Моля, използвайте друго.")
                return render(request, 'auth/register.html', {'form': form})
            if User.objects.filter(email = email).exists():
                messages.error(request, "Този емайл е вече в употреба! Моля, използвайте друг.")
                return render(request, 'auth/register.html', {'form': form})
            
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    nickname=nickname,
                    email = email
                    )
                models.UserProfile.objects.create(
                    user = user
                )
            except Exception as user_register_error:
                messages.error(request, "Не успяхме да създадем профил! Моля, опитайте отново.")
                print(f"Error while registering user account: {user_register_error}")
                return render(request, 'auth/register.html', {'form': form})
            
            return redirect('login')
    else:
        form = forms.RegisterForm()  
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect()
    return render(request, 'auth/logout.html')

def login_view(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if not User.objects.filter(username = username).exists():
                messages.error(request, 'Неправилно потребителско име или профил с това потребителско име не съществува.')
                return render(request, 'auth/login.html', {'form':form})
            
            user = authenticate(username = username, password = password)
            
            if user is None:
                messages.error(request, 'Възникна грешка! Моля опитайте отново.')
                return render(request, 'auth/login.html', {'form':form})
            else:
                login(request, user)
                messages.success(request, "Успешно влизане в профила!")
                return redirect('dashboard')
    else:
        form = forms.LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def account_view(request):
    user = request.user
    context = {
        "user": user,
        "profile": models.UserProfile.objects.filter(user = user)
    }
    return render(request, 'auth/account.html', context)

def account_delete(request):
    user = request.user
    if request.method == "POST":
        user_model_reference = User.objects.filter(username = user.username)
        user_model_reference.delete()
        return redirect('register')
    return render(request, 'auth/account_delete.html')

#* ===== APP ===== *#
def dashboard(request):
    return render(request, 'app/dashboard.html')

def map_view(request):
    beaches = models.Beach.objects.filter(has_been_approved=True)
    context = {
        "beaches": list(beaches.values("id", "latitude", "longitude"))
    }
    return render(request, "app/map.html", context)

def beach_data(request, beach_id):
    beach = models.Beach.objects.get(id=beach_id)
    return JsonResponse({
        "pk": str(beach.pk),
        "name": beach.name,
        "description": beach.description,
        "has_lifeguard": beach.has_lifeguard,
        "has_parking": beach.has_parking,
        "has_paid_parking": beach.has_paid_parking,
        "has_paid_zone": beach.has_paid_zone,
        "has_beach_bar": beach.has_beach_bar,
        "has_toilets": beach.has_toilets,
        "has_changing_rooms": beach.has_changing_rooms
    })
    
def beach_add(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if request.method == "POST":
        form = forms.BeachAddForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.cleaned_data['image']
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            has_lifeguard = form.cleaned_data['has_lifeguard']
            has_parking = form.cleaned_data['has_parking']
            has_paid_parking = form.cleaned_data['has_paid_parking']
            has_toilets = form.cleaned_data['has_toilets']
            has_changing_rooms = form.cleaned_data['has_changing_rooms']
            has_paid_zone = form.cleaned_data['has_paid_zone']
            has_beach_bar = form.cleaned_data['has_beach_bar']

            try:
                models.Beach.objects.create(
                    name=name,
                    description=description,
                    has_lifeguard=has_lifeguard,
                    has_parking=has_parking,
                    has_paid_parking=has_paid_parking,
                    has_toilets=has_toilets,
                    has_changing_rooms=has_changing_rooms,
                    has_paid_zone=has_paid_zone,
                    has_beach_bar=has_beach_bar,
                    latitude=request.POST.get('latitude'),
                    longitude=request.POST.get('longitude')
                )
                messages.success(
                    request,
                    'Добавите плаж успешно. Изчаква одобрение от администратор.'
                )
                return redirect('map')
            except Exception as e:
                print(f"Error while trying to add a beach: {e}")
                messages.error(
                    request,
                    'Нещо се обърка! Не успяхме да добавим този плаж към картата. Моля, опитайте отново'
                )
                return render(request, 'app/beaches/beach_add.html', {'form': form})
    else:
        form = forms.BeachAddForm(initial={'latitude': lat, 'longitude': lng})

    return render(request, 'app/beaches/beach_add.html', {'form': form})


#* ===== MODERATION ===== *#
@user_passes_test(is_moderator)
def dashboard_mod(request):
    pending_beaches = models.Beach.objects.filter(has_been_approved=False)
    reports = models.BeachReport.objects.filter(resolved = False)
    context = {
        'pending': pending_beaches,
        'reports': reports
    }
    return render(request, 'app/moderator/dashboard_mod.html', context)

@user_passes_test(is_moderator)
def mark_as_approved(request, beach_id):
    beach = get_object_or_404(models.Beach, id = beach_id)
    beach.has_been_approved = True
    beach.approved_date = timezone.now()
    beach.save()
    
#* ====== BEACH REPORTING ===== *#
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
                models.BeachReport.objects.create(
                    beach = beach,
                    submitted_by = user,
                    title = title,
                    description = description,
                    category = category
                )
                messages.success(request, 'Успешно подадено докладване!')
                return redirect('map')
            except Exception as e:
                print(f"Error while trying to submit report: {e}")
                messages.error(request, 'Възникна грешка! Моля, опитайте отново.')
                return render(request, 'app/reports/report_add.html', {'form': form})
    else:
        form = forms.ReportBeachForm()
    
    return render(request, 'app/reports/report_add.html', {'form':form})

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

def log_beach(request, beach_id):
    if request.method == "POST":
        pass
    else:
        form = forms.LO
    return render(request, 'app/log/log_add.html')