from django.urls import path

from . import views


urlpatterns = [
    path(
        "clients/",
        views.client_list,
        name="client_list",
    ),

    path(
        "clients/<int:client_id>/",
        views.client_detail,
        name="client_detail",
    ),

    path(
        "clients/<int:client_id>/projects/create/",
        views.project_create,
        name="project_create",
    ),

    path(
        "projects/<int:project_id>/",
        views.project_detail,
        name="project_detail",
    ),

    path(
        "projects/<int:project_id>/update/",
        views.project_update,
        name="project_update",
    ),

    path(
        "convert-lead/<int:lead_id>/",
        views.convert_lead_to_client,
        name="convert_lead_to_client",
    ),
]