from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from beaches import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    
    #* APP URLS
    path('', include('beaches.urls')),

    #* MODERATION
    path('moderation/dashboard-mod/', views.dashboard_mod, name='dashboard_mod'),
    path('moderation/dashboard/beach/delete/<uuid:beach_id>/', views.delete_beach, name='beach_delete'),
    path('moderation/dashboard/beach/approve/<uuid:beach_id>/', views.mark_as_approved, name='beach_approve'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)