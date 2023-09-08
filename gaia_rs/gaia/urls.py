from django.urls import path

from . import views


app_name = 'maps'

urlpatterns = [
    path('wmts_map/', views.wmts_map, name='wmts_map'),
    path('map_form/', views.map_form, name='map_form'),
]