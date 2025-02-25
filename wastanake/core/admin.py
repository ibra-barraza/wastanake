from django.contrib import admin
from .models import Terrain

@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'size', 'soil_type', 'ph_level']
    list_filter = ['soil_type', 'user']
    search_fields = ['name', 'user__username', 'location']
    readonly_fields = ['created_at']

    fieldsets = (
        (None, {'fields': ('user', 'name')}),
        ('Detalles del Terreno', {
            'fields': ('size', 'soil_type', 'ph_level', 'location')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )