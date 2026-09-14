from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.campaign_list,
        name="campaign_list",
    ),

    path(
        "create/",
        views.campaign_create,
        name="campaign_create",
    ),

    path(
        "<int:campaign_id>/",
        views.campaign_detail,
        name="campaign_detail",
    ),

    path(
    "<int:campaign_id>/generate/",
    views.generate_campaign_messages,
    name="generate_campaign_messages",
    ),
    
]