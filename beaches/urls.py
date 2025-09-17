from django.urls import path
from . import views

urlpatterns = [
    path(' ', views.redirect_view, name='redirect'),
    #* AUTHENTICATION URLS:
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/confirm', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),
    path('password-reset/', views.reset_password, name="reset_password"),
    #* EMAIL CONFIRMATION/RESETTING RELATED:
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path("password/reset/enter-mail/", views.enter_mail, name="enter_mail"),
    path("password/reset/<uidb64>/<token>/", views.set_new_password_from_mail, name='set_new_password_from_mail'),
    #* APP URLS:
    path('dashboard/', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map'),
    path("beach/<uuid:beach_id>/", views.beach_data, name="beach_data"),
    path('beach/add/', views.beach_add, name='beach_add'),
    #* MODERATION:
    path('moderation/dashboard/', views.dashboard_mod, name='dashborad_mod'),
    #* REPORTING:
    path("report-beach/<uuid:beach_id>/", views.report_beach, name="report_beach"),
    path('report-beach/mark-as-resolved/<uuid:report_id>/', views.report_mark_as_resolved, name="report_resolve"),
    path('report-beach/delete/<uuid:report_id>/', views.report_delete, name='report_delete'),
    #* LOGGING & LOGS:
    path('log-beach/<uuid:beach_id>/', views.log_beach, name='log_beach'),
    path('logs/today/<uuid:beach_id>/', views.view_logs_spec, name='log_beach_spec'),
    path('logs/my-logs/all/', views.view_my_logs, name='my_logs'),
    #* MISC:
    path('account/setup/', views.enter_details, name='enter_details'),
]