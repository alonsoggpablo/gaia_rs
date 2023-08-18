from django.contrib.gis import admin

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

class DataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands',)
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    ordering = ('name',)
    def get_actions(self, request):
        actions = super(DataCubeAdmin, self).get_actions(request)

        actions['get_ncdf'] = (get_ncdf, 'get_ncdf', 'Get Satellite Data')
        actions['get_ndvi'] = (get_ndvi, 'get_ndvi', 'Generate NDVI GeoTIFF Files')
        actions['get_bsi'] = (get_bsi, 'get_bsi', 'Generate BSI GeoTIFF Files')


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
class GeoImageAdmin(admin.GISModelAdmin):
    exclude = ('name','processing_date','observing_date')
    list_display = ('name','processing_date','observation_date')
    list_filter = ('datacube','name','observation_date',)
    ordering = ('name','observation_date')
    def display_image(self,obj):
        return '<img src="%s" width="100" height="100" />' % (obj.image.url)
    display_image.allow_tags = True
    display_image.short_description = 'Image'
admin.site.register(GeoImage,GeoImageAdmin)



