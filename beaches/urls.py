from django.urls import path
from . import views

urlpatterns = [
    #* AUTHENTICATION URLS
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/confirm', views.logout_view, name='logout'),
    #* APP URLS
    path('app/dashboard/', views.dashboard, name='dashboard')
    #* MISC
]