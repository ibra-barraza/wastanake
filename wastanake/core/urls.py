from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agregar-terreno/', views.add_terrain, name='add_terrain'),
]