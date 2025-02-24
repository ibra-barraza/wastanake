from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Terrain
from .forms import TerrainForm

@login_required
def home(request):
    terrains = Terrain.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/home.html', {'terrains': terrains})

@login_required
def add_terrain(request):
    if request.method == 'POST':
        form = TerrainForm(request.POST)
        if form.is_valid():
            terrain = form.save(commit=False)
            terrain.user = request.user
            terrain.save()
            return redirect('home')
    else:
        form = TerrainForm()
    return render(request, 'core/add_terrain.html', {'form': form})