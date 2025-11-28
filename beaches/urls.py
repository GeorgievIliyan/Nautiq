from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    #* AUTHENTICATION URLS:
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/confirm', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),
    path('account/delete/', views.account_delete, name='delete_account'),
    #* APP URLS:
    path('dashboard/', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map'),
    path("beach/<uuid:beach_id>/", views.beach_data, name="beach_data"),
    path('favourites/', views.favourite_beaches, name='favourites'),
    #* REPORTING:
    path("report-beach/<uuid:beach_id>/", views.report_beach, name="report_beach"),
    path('report-beach/mark-as-resolved/<uuid:report_id>/', views.report_mark_as_resolved, name="report_resolve"),
    path('report-beach/delete/<uuid:report_id>/', views.report_delete, name='report_delete'),
    #* LOGGING & LOGS:
    path('logs/today/<uuid:beach_id>/', views.view_logs_spec, name='log_beach_spec'),
    path('logs/my-logs/all/', views.view_my_logs, name='my_logs'),
    #* GAMIFICATION
    path("tasks/", views.tasks_view, name="tasks"),
    path("tasks/accept/<int:task_id>/", views.accept_task, name="accept_task"),
    path("tasks/complete/<int:task_id>/", views.complete_task, name="complete_task"),
    #* MISC:
    path('account/setup/', views.enter_details, name='enter_details'),
    path('settings/', views.app_settings, name='settings'),
    path('terms/', views.terms, name="terms"),
    path('', views.redirect_from_empty_link, name='redirect_from_empty_link')
]