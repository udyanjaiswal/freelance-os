from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('discover/', include('discovery.urls')),
    path('leads/', include('leads.urls')),
    path('outreach/', include('outreach.urls')),
    path('projects/', include('projects.urls')),
]