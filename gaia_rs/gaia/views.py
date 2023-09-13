import os

from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from .models import MapLayer, GeoImage
from .models import DataCube
from .forms import DataCubeForm
from django.contrib.gis.geos import Polygon
import json
from .tables import DataCubeTable, DataCubeDetailTable, GeoImageTable
from django.conf import settings


def index(request):
    items=DataCube.objects.all()
    table=DataCubeTable(items)
    return render(request, 'index.html',{'table':table})


def map_form(request):
    if request.method == 'POST':
        form = DataCubeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gaia:index')
    else:
        form=DataCubeForm()

    return render(request,f'map_form.html',{'form':form})

def datacube_detail(request, pk):
    datacube = DataCube.objects.get(pk=pk)
    geoimages=GeoImage.objects.filter(datacube=datacube)
    datacube_table=DataCubeDetailTable([datacube])
    geoimages_table=GeoImageTable(datacube=datacube)
    polygon_centroid = datacube.spatial_extent.centroid
    center_latitude=polygon_centroid.y
    center_longitude=polygon_centroid.x
    return render(request, 'datacube_detail.html', {'geoimages_table':geoimages_table,'datacube_table': datacube_table,'center_latitude':center_latitude,'center_longitude':center_longitude,'datacube':datacube,'geoimages':geoimages})

def raster_file(request,pk):
    geoimage = GeoImage.objects.get(pk=pk)
    polygon_centroid = geoimage.datacube.spatial_extent.centroid
    center_latitude = polygon_centroid.y
    center_longitude = polygon_centroid.x
    return render(request, 'raster_file.html', {'geoimage': geoimage,'center_latitude':center_latitude,'center_longitude':center_longitude})

def process_datacube(request,pk):
    datacube = DataCube.objects.get(pk=pk)
    datacube.get_ncdf()
    dataproduct_script=datacube.dataproduct.script

    func=globals()[dataproduct_script.name]
    datacube.func()

    return render(request, 'datacube_detail.html', {'pk': pk})


def serve_geotiff(request, file_name):
    # Construct the path to the GeoTIFF file
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file and serve it using FileResponse
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            return response

    # Handle the case where the file doesn't exist
    return HttpResponseNotFound("File not found")



