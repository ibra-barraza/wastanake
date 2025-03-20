from difflib import get_close_matches
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from googletrans import Translator
import requests
import pandas as pd
from .models import Terrain
from .forms import TerrainForm

@login_required
def home(request):
    terrains = Terrain.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/home.html', {'terrains': terrains})

@login_required
def add_terrain(request):
    current_lat = None
    current_lon = None
    default_lat = 27.4828  # Latitud de Cd. Obregón, Sonora
    default_lon = -109.9339  # Longitud de Cd. Obregón, Sonora

    if request.method == 'POST':
        form = TerrainForm(request.POST)
        if form.is_valid():
            terrain = form.save(commit=False)
            terrain.user = request.user
            terrain.save()
            return redirect('home')
    else:
        form = TerrainForm()

    return render(request, 'core/add_terrain.html', {
        'form': form,
        'current_lat': current_lat,
        'current_lon': current_lon,
        'default_lat': default_lat,
        'default_lon': default_lon,
    })

@login_required
def edit_terrain(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id, user=request.user)
    if request.method == 'POST':
        form = TerrainForm(request.POST, instance=terrain)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TerrainForm(instance=terrain)
    return render(request, 'core/edit_terrain.html', {'form': form, 'terrain': terrain})

@login_required
def add_terrain(request):
    current_lat = None
    current_lon = None
    default_lat = 27.4828  # Latitud de Cd. Obregón, Sonora
    default_lon = -109.9339  # Longitud de Cd. Obregón, Sonora

    if request.method == 'POST':
        form = TerrainForm(request.POST)
        if form.is_valid():
            terrain = form.save(commit=False)
            terrain.user = request.user
            terrain.save()
            return redirect('home')
    else:
        form = TerrainForm()

    return render(request, 'core/add_terrain.html', {
        'form': form,
        'current_lat': current_lat,
        'current_lon': current_lon,
        'default_lat': default_lat,
        'default_lon': default_lon,
    })
    
@login_required
def delete_terrain(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id, user=request.user)
    if request.method == 'POST':
        terrain.delete()
        return redirect('home')
    return render(request, 'core/delete_terrain.html', {'terrain': terrain})
    

@login_required
def terrain_analysis(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id, user=request.user)
    
    temp_min, temp_max = get_weather(terrain.latitude, terrain.longitude)
    print(f'Temp Min: {temp_min}°C, Temp Max: {temp_max}°C')
    print(f'Zona Climática: {terrain.climate_zone}')
    crops = get_crops(temp_min, temp_max, terrain.climate_zone) if temp_min is not None and temp_max is not None else []
    
    return render(request, 'core/terrain_analysis.html', {
        'terrain': terrain,
        'crops': crops
    })

def get_weather(lat, lon):
    API_KEY = ''
    DAYS = 1

    URL = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days={DAYS}&aqi=no&alerts=no&lang=es'
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Recomendación para {data['location']['name']}, {data['location']['country']}")
        forecast = data['forecast']['forecastday'][0]
        return forecast['day']['mintemp_c'], forecast['day']['maxtemp_c']
    
    return None, None

def load_csv(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='iso-8859-1')

def get_matching_item(names, faostat_items):
    for name in names:
        matches = get_close_matches(name, faostat_items)
        if matches:
            return matches[0].capitalize()
    return None

def get_crops(temp_min, temp_max, climate_zone):
    ecocrop_df = load_csv('EcoCrop_DB.csv')
    faostat_df = load_csv('FAOSTAT_producer_prices.csv')

    # Filtrar por temperaturas
    filtered_crops = ecocrop_df[
        (temp_min >= ecocrop_df['TMIN']) & 
        (temp_max <= ecocrop_df['TMAX'])
    ]
    
    # Filtrar por nombres comunes
    filtered_crops.loc[:, 'COMNAME'] = filtered_crops['COMNAME'].fillna('').apply(lambda x: [name.strip().lower() for name in x.split(',')] if x else [])
    
    # Filtrar por zona climática
    filtered_crops = filtered_crops[filtered_crops['CLIZ'].astype(str).apply(lambda x: climate_zone in x.split(','))]

    # Filtrar por coincidencias de nombres comunes en FAOSTAT
    faostat_items = set(faostat_df['Item'].str.lower().unique())
    filtered_crops['FAOSTAT_MATCH'] = filtered_crops['COMNAME'].apply(lambda names: get_matching_item(names, faostat_items))
    matching_crops = filtered_crops.dropna(subset=['FAOSTAT_MATCH'])
    
    if matching_crops.empty:
        print("Advertencia: No se encontraron coincidencias entre los cultivos y FAOSTAT.")
        return []
    
    translator = Translator()
    return [translator.translate(name, src='en', dest='es').text for name in matching_crops['FAOSTAT_MATCH'].unique()]
