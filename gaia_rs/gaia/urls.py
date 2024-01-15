from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import LoginView,LogoutView


app_name = 'gaia'

urlpatterns = [
    path('', views.DataCubeListView.as_view(), name='index'),
    path('dataproducts', views.DataProductsListView.as_view(), name='dataproducts'),
    path('map_form/', views.map_form, name='map_form'),
    path('datacube_detail/<int:pk>/', views.datacube_detail, name='datacube_detail'),
    path('process_datacube/<int:pk>/', views.process_datacube, name='process_datacube'),
    path('raster_file/<int:pk>/', views.raster_file, name='raster_file'),
    path('media/raster_files/<str:file_name>/', views.serve_geotiff, name='serve_geotiff'),
    path('get_status/<int:record_id>/', views.get_status, name='get_status'),
    path('get_puntos/<int:record_id>/', views.get_puntos, name='get_puntos'),
    path('media/plot_images/<str:plot_image>/', views.view_png, name='view_png'),
    path('datacube_edit/<int:pk>/', views.datacube_edit, name='datacube_edit'),
    path('delete_geoimage/<int:pk>/', views.delete_geoimage, name='delete_geoimage'),
    path('delete_datacube/<int:pk>/', views.delete_datacube, name='delete_datacube'),
    path('raster_file_download/<int:pk>/', views.raster_file_download, name='raster_file_download'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)