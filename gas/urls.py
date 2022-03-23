from django.contrib import admin
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path("", views.index, name="index"),  
    path("product/<int:pk>", views.single_product)
    # path("lipa_na_mpesa_online/<int:pk>", views.lipa_na_mpesa_online, name="lipa_na_mpesa_online")
]