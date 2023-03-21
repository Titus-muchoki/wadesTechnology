from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("product/<int:pk>", views.single_product),
    path("addToCart/<int:pk>", views.addToCart, name="addToCart"),
    path("removeFromCart/<int:pk>", views.removeFromCart, name="removeFromCart"),
    path("cart/", views.cart_items, name="cartItems"),
     path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('register/', views.register, name='register'),
    # path("lipa_na_mpesa_online/", views.lipa_na_mpesa_online, name="lipa_na_mpesa_online")
]