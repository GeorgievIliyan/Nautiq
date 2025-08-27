from django.urls import path
from . import views

urlpatterns = [
    #* AUTHENTICATION URLS
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/confirm', views.logout_view, name='logout'),
    #* APP URLS
    path('app/dashboard/', views.dashboard, name='dashboard'),
    path('app/map/', views.map_view, name='map'),
    path("app/beach/<int:beach_id>/", views.beach_data, name="beach_data"),
    path('app/beach/add/', views.beach_add, name='beach_add')
    #* MISC
]