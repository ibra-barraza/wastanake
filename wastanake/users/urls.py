from django.urls import path
from django.contrib.auth.views import LogoutView  # <-- Añade esto
from .views import register, custom_login

urlpatterns = [
    path('registro/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]