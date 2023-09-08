from django.shortcuts import render, redirect
from .models import MapLayer
from .models import DataCube
from .forms import DataCubeForm
from django.contrib.gis.geos import Polygon
import json

def wmts_map(request):
    map_layer=MapLayer.objects.first()
    return render(request, 'wmts_map.html', {'map_layer': map_layer})

def map_form(request):
    if request.method == 'POST':
        form = DataCubeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/wmts_map')
    else:
        form=DataCubeForm()

    return render(request,f'map_form.html',{'form':form})



