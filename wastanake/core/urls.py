from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('agregar-terreno/', views.add_terrain, name='add_terrain'),
    path('editar-terreno/<int:terrain_id>/', views.edit_terrain, name='edit_terrain'),
    path('eliminar-terreno/<int:terrain_id>/', views.delete_terrain, name='delete_terrain'),
    path('analisis-terreno/<int:terrain_id>/', views.terrain_analysis, name='terrain_analysis'),
]