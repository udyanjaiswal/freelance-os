from django.urls import path
from . import views

urlpatterns = [
    path("import/", views.import_leads, name="import_leads"),
    path("export/", views.export_leads, name="export_leads"),

    path("<int:lead_id>/", views.lead_detail, name="lead_detail"),
    path(
        "<int:lead_id>/status/",
        views.update_status,
        name="update_status",
    ),
    path(
        "<int:lead_id>/outreach/",
        views.add_outreach,
        name="add_outreach",
    ),
]