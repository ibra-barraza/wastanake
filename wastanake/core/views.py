from datetime import date, datetime, timedelta
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
def select_analysis_dates(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id, user=request.user)
    return render(request, 'core/select_analysis_dates.html', {'terrain': terrain})

@login_required
def terrain_analysis(request, terrain_id):
    terrain = get_object_or_404(Terrain, id=terrain_id, user=request.user)
    
    date_range = request.POST.get('date_range')
    dates = date_range.split()
    if len(dates) == 0:
        start_date, end_date = 2 * [date.today().strftime("%Y-%m-%d")]
    elif len(dates) == 1:
        start_date, end_date = 2 * [dates[0]]
    else:
        start_date, end_date = dates[0], dates[2]
    print(f'Inicio: {start_date}, Fin: {end_date}')
    
    temp_min, temp_max = get_weather(start_date, end_date, terrain.latitude, terrain.longitude)
    print(f'Temp Min: {temp_min}°C, Temp Max: {temp_max}°C')
    print(f'Zona Climática: {terrain.climate_zone}')
    crops = get_crops(temp_min, temp_max, terrain.climate_zone, terrain.ph_level) if temp_min is not None and temp_max is not None else []
    
    return render(request, 'core/terrain_analysis.html', {
        'terrain': terrain,
        'start_date': start_date,
        'end_date': end_date,
        'crops': crops,
    })

def get_weather(start_date, end_date, lat, lon):
    API_KEY = ''

    today = datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    sum_temp_min, sum_temp_max = 0, 0
    
    if (start - today).days + 1 <= 14:
        total_days = (end - start).days + (start - today).days

        days_forecast = min((end - today).days + 1, 14)
        
        url_forecast = f'https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days={days_forecast}&lang=es'
        response = requests.get(url_forecast)
        
        if response.status_code != 200:
            print('1. Error: No se pudo obtener los datos de forecast.')
            print(response.json())
            return None, None
        
        data = response.json()
        print(f"Recomendación para {data['location']['name']}, {data['location']['country']}")
        
        for i, forecast in enumerate(data['forecast']['forecastday']):
            forecast_date = datetime.strptime(forecast['date'], "%Y-%m-%d")
            if forecast_date >= start:
                sum_temp_min += forecast['day']['mintemp_c']
                sum_temp_max += forecast['day']['maxtemp_c']
        
        remaining_days = total_days - days_forecast
        
        if remaining_days > 0:
            for i in range(remaining_days):
                dt = (today + timedelta(days=days_forecast + i + 1)).strftime("%Y-%m-%d")
                url_future = f'https://api.weatherapi.com/v1/future.json?key={API_KEY}&q={lat},{lon}&dt={dt}&lang=es'
                response = requests.get(url_future)
                
                if response.status_code != 200:
                    print('1. Error: No se pudo obtener los datos de future.')
                    print(response.json())
                    return None, None
                
                data = response.json()
                forecast = data['forecast']['forecastday'][0]
                sum_temp_min += forecast['day']['mintemp_c']
                sum_temp_max += forecast['day']['maxtemp_c']
        
        total_days = (end - start).days + 1
    else:
        total_days = (end - start).days + 1
        for i in range(total_days):
            dt = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            url_future = f'https://api.weatherapi.com/v1/future.json?key={API_KEY}&q={lat},{lon}&dt={dt}&lang=es'
            response = requests.get(url_future)
            
            if response.status_code != 200:
                print('2. Error: No se pudo obtener los datos de future.')
                print(response.json())
                return None, None
            
            data = response.json()
            forecast = data['forecast']['forecastday'][0]
            sum_temp_min += forecast['day']['mintemp_c']
            sum_temp_max += forecast['day']['maxtemp_c']
    
    temp_min_avg = sum_temp_min / total_days
    temp_max_avg = sum_temp_max / total_days
    
    return temp_min_avg, temp_max_avg

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

def process_metric(df, metric_name):
    metric_df = df[df['Element'] == metric_name].copy()
    metric_df['Value'] = pd.to_numeric(metric_df['Value'], errors='coerce')
    metric_df = metric_df.dropna(subset=['Value'])
    
    grouped = metric_df.groupby('Item').agg({
        'Value': ['mean', 'count'],
        'Unit': 'first'
    })
    grouped.columns = [f'{metric_name}_{stat}' if stat != 'first' else f'{metric_name}_Unit' for stat in grouped.columns.get_level_values(1)]
    return grouped.reset_index()

def translate_and_unique_items(raw_result):
    unique_items = {}
    translator = Translator()
    
    for entry in raw_result:
        item = entry['Item']
        if item not in unique_items:
            try:
                translated_name = translator.translate(item, src='en', dest='es').text
                entry['Item'] = translated_name
            except Exception as e:
                print(f"Error traduciendo {item}: {str(e)}")
                entry['Item'] = item
            unique_items[item] = entry
    
    return list(unique_items.values())

def get_crops(temp_min, temp_max, climate_zone, ph_level):
    ecocrop_df = load_csv('EcoCrop_DB.csv')
    producer_prices_df = load_csv('FAOSTAT_producer_prices.csv')
    crops_and_livestock_df = load_csv('FAOSTAT_crops_and_livestock_products.csv')
    weights = {
        'Avg_Price_Norm': 0.4,
        'Yield_mean_Norm': 0.3,
        'Production_mean_Norm': 0.3
    }

    filtered_crops = ecocrop_df[
        (temp_min >= ecocrop_df['TMIN']) & (temp_max <= ecocrop_df['TMAX']) &
        (float(ph_level) >= ecocrop_df['PHMIN']) & (float(ph_level) <= ecocrop_df['PHMAX'])
    ]
    filtered_crops.loc[:, 'COMNAME'] = filtered_crops['COMNAME'].fillna('').apply(lambda x: [name.strip().lower() for name in x.split(',')] if x else [])
    filtered_crops = filtered_crops[filtered_crops['CLIZ'].astype(str).apply(lambda x: climate_zone in x.split(','))]
    faostat_items = set(producer_prices_df['Item'].str.lower().unique())
    filtered_crops['FAOSTAT_MATCH'] = filtered_crops['COMNAME'].apply(lambda names: get_matching_item(names, faostat_items))
    
    matching_crops = filtered_crops.dropna(subset=['FAOSTAT_MATCH'])
    if matching_crops.empty:
        print("Advertencia: No se encontraron coincidencias entre los cultivos y FAOSTAT.")
        return []
    
    producer_prices_df['Value'] = pd.to_numeric(producer_prices_df['Value'], errors='coerce')
    price_data = producer_prices_df.dropna(subset=['Value'])
    
    if not price_data.empty:
        crop_price_df = price_data.groupby('Item').agg({
            'Value': ['mean', 'count'],
            'Unit': 'first'
        }).reset_index()
        crop_price_df.columns = ['Item', 'Avg_Price', 'Price_Count', 'Unit']
        crop_price_df = crop_price_df[crop_price_df['Price_Count'] >= 1]
    
    yield_stats = process_metric(crops_and_livestock_df, 'Yield')
    production_stats = process_metric(crops_and_livestock_df, 'Production')
    
    combined_stats = pd.merge(
        crop_price_df,
        yield_stats,
        on='Item',
        how='left'
    ).merge(
        production_stats,
        on='Item',
        how='left'
    )
    
    matching_items = matching_crops['FAOSTAT_MATCH'].unique()
    combined_stats = combined_stats[combined_stats['Item'].str.lower().isin([item.lower() for item in matching_items])]
    
    metrics_to_normalize = ['Avg_Price', 'Yield_mean', 'Production_mean']
    for metric in metrics_to_normalize:
        if metric in combined_stats.columns:
            combined_stats[f'{metric}_Norm'] = (
                (combined_stats[metric] - combined_stats[metric].min()) / 
                (combined_stats[metric].max() - combined_stats[metric].min()) * 100
            )
    
    combined_stats['Final_Score'] = 0
    for metric, weight in weights.items():
        if metric in combined_stats.columns:
            combined_stats['Final_Score'] += combined_stats[metric] * weight
    
    if not combined_stats.empty:
        combined_stats['Final_Score'] = (
            (combined_stats['Final_Score'] - combined_stats['Final_Score'].min()) / 
            (combined_stats['Final_Score'].max() - combined_stats['Final_Score'].min()) * 100
        )
    
    final_ranking = combined_stats[[
        'Item', 'Avg_Price', 'Yield_mean', 'Production_mean', 'Final_Score'
    ]].sort_values('Final_Score', ascending=False).reset_index(drop=True)
    
    item_case_mapping = {item.lower(): item for item in final_ranking['Item'].unique()}
    matching_crops['FAOSTAT_ITEM'] = matching_crops['FAOSTAT_MATCH'].str.lower().map(item_case_mapping)

    merged_data = pd.merge(
        matching_crops,
        final_ranking,
        left_on='FAOSTAT_ITEM',
        right_on='Item',
        how='left'
    )

    raw_result = merged_data[['FAOSTAT_ITEM', 'COMNAME', 'Avg_Price', 'Yield_mean', 'Production_mean', 'Final_Score']] \
        .rename(columns={'FAOSTAT_ITEM': 'Item', 'COMNAME': 'Match'}) \
        .sort_values(by='Final_Score', ascending=False) \
        .to_dict(orient='records')
    
    result = translate_and_unique_items(raw_result)
    
    return result
