import os

from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .filters import DataCubeFilter
from .models import MapLayer, GeoImage
from .models import DataCube
from .forms import DataCubeForm
from django.contrib.gis.geos import Polygon
import json
from .tables import DataCubeTable, DataCubeDetailTable, GeoImageTable
from django.conf import settings
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

def index(request):
    items=DataCube.objects.all()
    table=DataCubeTable(items)
    return render(request, 'index.html',{'table':table,'filter':DataCubeTable.Meta.filterset_class})

class DataCubeListView(SingleTableMixin,FilterView):
    table_class = DataCubeTable
    model=DataCube
    template_name = 'index.html'
    filterset_class = DataCubeFilter

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
    plot_image=""
    try:
        plot_image=datacube.plot_image.url
    except:
        pass
    polygon_centroid = datacube.spatial_extent.centroid
    center_latitude=polygon_centroid.y
    center_longitude=polygon_centroid.x
    return render(request, 'datacube_detail.html', {'plot_image':plot_image,'geoimages_table':geoimages_table,'datacube_table': datacube_table,'center_latitude':center_latitude,'center_longitude':center_longitude,'datacube':datacube,'geoimages':geoimages})

def raster_file(request,pk):
    geoimage = GeoImage.objects.get(pk=pk)
    polygon_centroid = geoimage.datacube.spatial_extent.centroid
    center_latitude = polygon_centroid.y
    center_longitude = polygon_centroid.x
    return render(request, 'raster_file.html', {'geoimage': geoimage,'center_latitude':center_latitude,'center_longitude':center_longitude})

def process_datacube(request,pk):
    datacube = DataCube.objects.get(pk=pk)
    datacube.status='processing'
    datacube.save()
    datacube.get_ncdf()
    datacube_table=DataCubeDetailTable([datacube])
    geoimages_table=GeoImageTable(datacube=datacube)
    polygon_centroid = datacube.spatial_extent.centroid
    center_latitude = polygon_centroid.y
    center_longitude = polygon_centroid.x

    # dataproduct_script=str(datacube.dataproduct.script)
    # func=getattr(datacube,dataproduct_script)
    # func()

    return render(request, 'datacube_detail.html', {'pk': pk,'datacube_table': datacube_table,'datacube':datacube,'geoimages_table':geoimages_table,'center_latitude':center_latitude,'center_longitude':center_longitude})
    #return render (request,'processing_datacube.html',{'datacube':str(datacube.name)})

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

def get_status(request, record_id):
    # Fetch the updated text for the record with the given ID
    datacube=DataCube.objects.get(pk=record_id)
    status=datacube.status
    if status=='file_downloaded':
        # Create a reverse URL to the datacube detail view
        url = reverse('gaia:datacube_detail', kwargs={'pk': record_id})

        # Create a button element with the redirect URL
        status = """
                   <a href='{}' class='btn btn-primary btn-sm'>Results</a>
               """.format(url)
        datacube.status='-'
        datacube.save()
    return HttpResponse(status)

def get_puntos(request,record_id):
    datacube=DataCube.objects.get(pk=record_id)
    status=datacube.status
    puntos=""
    if status=='finished' or status=='created' or status=='error' or status=='' or status=='file_downloaded':
        puntos=""
    else:
        puntos="..."


    return HttpResponse(puntos)

def view_png(request,plot_image):
    file_path = os.path.join(settings.MEDIA_ROOT, plot_image)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            return response
    else:
        return HttpResponse('File not found', status=404)

def datacube_edit(request,pk):
    datacube = DataCube.objects.get(pk=pk)
    if request.method == 'POST':
        form = DataCubeForm(request.POST,instance=datacube)
        if form.is_valid():
            form.save()
            return redirect('gaia:datacube_detail',pk=pk)
    else:
        form=DataCubeForm(instance=datacube)

    return render(request,f'map_form.html',{'form':form})


def delete_geoimage(request,pk):
    geoimage=GeoImage.objects.get(pk=pk)
    datacube=geoimage.datacube
    geoimage.delete()
    return redirect('gaia:datacube_detail',pk=datacube.pk)

def delete_datacube(request,pk):
    datacube=DataCube.objects.get(pk=pk)
    datacube.delete()
    return redirect('gaia:index')



