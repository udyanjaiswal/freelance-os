from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin-ukp/', admin.site.urls),

    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    
    path('discover/', include('discovery.urls')),
    path('leads/', include('leads.urls')),
    path('outreach/', include('outreach.urls')),
    path('projects/', include('projects.urls')),

    path(
        "terms/",
        TemplateView.as_view(template_name="terms.html"),
        name="terms",
    ),
]