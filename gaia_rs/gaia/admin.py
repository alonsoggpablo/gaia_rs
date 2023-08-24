import django.contrib.admin
from django.contrib.gis import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.db.backends.base import models
from leaflet.forms.widgets import LeafletWidget

# Register your models here.

from .models import WorldBorder, DataCube, Band, DataProduct, Category, Script, GeoImage

admin.site.register(WorldBorder,admin.GISModelAdmin)

def get_ncdf(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ncdf()

def get_ndvi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndvi()

def get_bsi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_bsi()

def get_rgb(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_rgb()

def get_ndci(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndci()

class DataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands',)
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    ordering = ('name',)
    def get_actions(self, request):
        actions = super(DataCubeAdmin, self).get_actions(request)

        actions['get_ncdf'] = (get_ncdf, 'get_ncdf', 'Get Satellite Data')
        actions['get_ndvi'] = (get_ndvi, 'get_ndvi', 'Generate NDVI GeoTIFF Files')
        actions['get_bsi'] = (get_bsi, 'get_bsi', 'Generate BSI GeoTIFF Files')
        actions['get_rgb'] = (get_rgb, 'get_rgb', 'Generate RGB Image Files')
        actions['get_ndci'] = (get_ndci, 'get_ndci', 'Generate NDCI GeoTIFF Files')


        return actions


admin.site.register(DataCube, DataCubeAdmin)
class BandAdmin(admin.GISModelAdmin):
    list_display = ('name', 'description','collection')
    list_filter = ('collection',)
    ordering = ('collection','name',)

admin.site.register(Band,BandAdmin)
class DataProductAdmin(admin.GISModelAdmin):
    list_display = ('name', 'category','script')
    list_filter = ('category','script')
    ordering = ('category','name',)

admin.site.register(DataProduct,DataProductAdmin)
class CategoryAdmin(admin.GISModelAdmin):
    ordering=('category',)

admin.site.register(Category,CategoryAdmin)
class ScriptAdmin(admin.GISModelAdmin):
    ordering=('script',)

admin.site.register(Script,ScriptAdmin)

class GeoImageAdmin(OSMGeoAdmin):
    exclude = ('name','processing_date','observation_date','datacube')
    list_display = ('name','processing_date','observation_date','raster_file')
    list_filter = ('datacube','name','observation_date',)
    ordering = ('name','observation_date')

    def datacube_spatial(self, obj):
        return obj.datacube.spatial_extent

admin.site.register(GeoImage,GeoImageAdmin)



