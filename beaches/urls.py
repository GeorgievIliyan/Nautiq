from django.urls import path
from . import views

urlpatterns = [
    #* AUTHENTICATION URLS
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/confirm', views.logout_view, name='logout'),
    #* APP URLS
    path('dashboard/', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map'),
    path("beach/<uuid:beach_id>/", views.beach_data, name="beach_data"),
    path('beach/add/', views.beach_add, name='beach_add'),
    #* MODERATION
    path('moderation/dashboard/', views.dashboard_mod, name='dashborad_mod'),
    #* REPORTING
    path("report-beach/<uuid:report_id>/", views.report_beach, name="report_beach"),
    path('report-beach/mark-as-resolved/<uuid:report_id>/', views.report_mark_as_resolved, name="report_resolve"),
    path('report-beach/delete/<uuid:report_id>/', views.report_delete, name='report_delete'),
    #* LOGGING
    path('log-beach/<uuid:beach_id>/', views.log_beach, name='log_beach')
    #* MISC
]