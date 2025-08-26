from django.shortcuts import render, redirect
from validators.numbers_validator import is_valid_number as has_number
from validators.uppercase_validator import is_valid_uppercase as has_uppercase
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from . import models
from . import forms

#* ===== AUTHENTICATION ===== *#

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

#* ===== APP ===== *#
def dashboard(request):
    return render(request, 'app/dashboard.html')