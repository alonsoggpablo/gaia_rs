from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'gaia'

urlpatterns = [
    path('', views.index, name='index'),
    path('map_form/', views.map_form, name='map_form'),
    path('datacube_detail/<int:pk>/', views.datacube_detail, name='datacube_detail'),
    path('process_datacube/<int:pk>/', views.process_datacube, name='process_datacube'),
    path('raster_file/<int:pk>/', views.raster_file, name='raster_file'),
    path('media/raster_files/<str:file_name>/', views.serve_geotiff, name='serve_geotiff'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)