from django.db import models
from users.models import CustomUser

class Terrain(models.Model):
    SOIL_TYPES = [
        ('ARCILLA', 'Arcilla'),
        ('ARENOSO', 'Arenoso'),
        ('LIMOSO', 'Limoso'),
        ('MIXTO', 'Mixto'),
    ]

    ZONE_TYPES = [
        ('tropical wet & dry (Aw)', 'Tropical húmedo y seco'),
        ('tropical wet (Ar)', 'Tropical húmedo'),
        ('desert or arid (Bw)', 'Desierto o árido'),
        ('steppe or semiarid (Bs)', 'Estepa o semiárido'),
        ('subtropical humid (Cf)', 'Subtropical húmedo'),
        ('subtropical dry summer (Cs)', 'Subtropical con verano seco'),
        ('subtropical dry winter (Cw)', 'Subtropical con invierno seco'),
        ('temperate oceanic (Do)', 'Templado oceánico'),
        ('temperate continental (Dc)', 'Templado continental'),
        ('temperate with humid winters (Df)', 'Templado con inviernos húmedos'),
        ('temperate with dry winters (Dw)', 'Templado con inviernos secos'),
        ('boreal (E)', 'Boreal'),
        ('polar (F)', 'Polar'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=10, decimal_places=2)  # En hectáreas
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPES)
    ph_level = models.DecimalField(max_digits=3, decimal_places=1)
    climate_zone = models.CharField(max_length=100, choices=ZONE_TYPES, default='tropical wet & dry (Aw)')
    latitude = models.DecimalField(max_digits=20, decimal_places=17, null=True, blank=True)  # Latitud
    longitude = models.DecimalField(max_digits=20, decimal_places=17, null=True, blank=True)  # Longitud
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.size} ha)"