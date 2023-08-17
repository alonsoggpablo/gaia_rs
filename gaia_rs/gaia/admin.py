from django.contrib.gis import admin

# Register your models here.

from .models import WorldBorder, DataCube, Band, DataProduct, Category, Script, GeoImage

admin.site.register(WorldBorder,admin.GISModelAdmin)
def get_ndvi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ndvi()

class DataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands',)
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    actions=[get_ndvi,]
    #actions = [get_tif,get_ncdf,get_ncdf_no_max_cloud,get_ncdf_cloud_mask]

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



