from django.contrib.gis import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import WorldBorder, DataCube, Band, DataProduct, Category, Script, GeoImage, MapLayer

# Register your models here.

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

def get_msi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_msi()

def get_evi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_evi()

def get_ndsi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndsi()

def get_ndwi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndwi()

def get_bais(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_bais()

def get_apa(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_apa()
def get_ndyi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndyi()

class DataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands','north','south','east','west','timeseries')
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover','plot_image')
    ordering = ('name',)
    def get_actions(self, request):
        actions = super(DataCubeAdmin, self).get_actions(request)

        actions['get_ncdf'] = (get_ncdf, 'get_ncdf', 'Get Satellite Data')
        actions['get_bais'] = (get_bais, 'get_bais', 'Disaster Fire raster files')
        actions['get_bsi'] = (get_bsi, 'get_bsi', 'Land BSI raster files')
        actions['get_ndwi'] = (get_ndwi, 'get_ndwi', 'Marine NDWI raster files')
        actions['get_apa'] = (get_ndvi, 'get_apa', 'Marine Algae raster files')
        actions['get_rgb'] = (get_rgb, 'get_rgb', 'RGB raster files')
        actions['get_ndsi'] = (get_ndsi, 'get_ndsi', 'Snow NDSI  raster files')
        actions['get_evi'] = (get_evi, 'get_evi', 'Vegetation EVI  raster files')
        actions['get_msi'] = (get_msi, 'get_msi', 'Vegetation MSI  raster files')
        actions['get_ndci'] = (get_ndci, 'get_ndci', 'Vegetation NDCI  raster files')
        actions['get_ndvi'] = (get_ndvi, 'get_ndvi', 'Vegetation NDVI raster files')
        actions['get_ndyi'] = (get_ndyi, 'get_ndyi', 'Vegetation NDYI raster files')

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
    ordering = ('category__category','name',)

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
    list_filter = ('datacube','datacube__dataproduct','processing_date','observation_date','name')
    ordering = ('name','observation_date')

    def datacube_spatial(self, obj):
        return obj.datacube.spatial_extent

admin.site.register(GeoImage,GeoImageAdmin)

admin.site.register(MapLayer,admin.GISModelAdmin)



