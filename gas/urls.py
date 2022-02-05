from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sign", views.signup, name="sign"),
    path("lipa_na_mpesa_online/<int:pk>", views.lipa_na_mpesa_online, name="lipa_na_mpesa_online")
]