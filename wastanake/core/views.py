from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
    return render(request, 'core/terrain_analysis.html', {'terrain': terrain})