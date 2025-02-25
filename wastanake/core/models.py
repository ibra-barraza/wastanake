from django.db import models
from users.models import CustomUser

class Terrain(models.Model):
    SOIL_TYPES = [
        ('ARCILLA', 'Arcilla'),
        ('ARENOSO', 'Arenoso'),
        ('LIMOSO', 'Limoso'),
        ('MIXTO', 'Mixto'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=10, decimal_places=2)  # En hectáreas
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES)
    ph_level = models.DecimalField(max_digits=3, decimal_places=1)
    latitude = models.DecimalField(max_digits=20, decimal_places=17, null=True, blank=True)  # Latitud
    longitude = models.DecimalField(max_digits=20, decimal_places=17, null=True, blank=True)  # Longitud
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.size} ha)"