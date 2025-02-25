from django import forms
from .models import Terrain

class TerrainForm(forms.ModelForm):
    class Meta:
        model = Terrain
        fields = ['name', 'size', 'soil_type', 'ph_level', 'latitude', 'longitude']
        labels = {
            'name': 'Nombre del Terreno',
            'size': 'Tamaño (hectáreas)',
            'soil_type': 'Tipo de Suelo',
            'ph_level': 'Nivel de pH',
            'latitude': 'Latitud',
            'longitude': 'Longitud'
        }
        widgets = {
            'ph_level': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '14'}),
            'size': forms.NumberInput(attrs={'placeholder': 'Ej: 5.5'}),
            'latitude': forms.NumberInput(attrs={'readonly': True}),
            'longitude': forms.NumberInput(attrs={'readonly': True}),
        }