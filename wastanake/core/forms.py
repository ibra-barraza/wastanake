from django import forms
from .models import Terrain

class TerrainForm(forms.ModelForm):
    class Meta:
        model = Terrain
        fields = ['name', 'size', 'soil_type', 'ph_level', 'location']
        labels = {
            'name': 'Nombre del Terreno',
            'size': 'Tamaño (hectáreas)',
            'soil_type': 'Tipo de Suelo',
            'ph_level': 'Nivel de pH',
            'location': 'Ubicación'
        }
        widgets = {
            'ph_level': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '14'}),
            'size': forms.NumberInput(attrs={'placeholder': 'Ej: 5.5'}),
        }