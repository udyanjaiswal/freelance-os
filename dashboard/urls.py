from django.urls import path

from . import views

urlpatterns = [

    path('', views.landing, name='landing'),

    path('app/', views.home, name='home'),

]