from django.contrib.gis import admin

# Register your models here.

from .models import WorldBorder, DataCube, Band, DataProduct, Category, Script

admin.site.register(WorldBorder,admin.GISModelAdmin)


def get_tif(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_tiff()

def get_evi(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_evi()

def get_ncdf(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ncdf()

def get_ncdf_cloud_mask(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ncdf_cloud_mask()

def get_ncdf_no_max_cloud(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.get_ncdf_without_max_cloud_cover()


class OpenEODataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands',)
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    actions = [get_tif,get_evi,get_ncdf,get_ncdf_no_max_cloud,get_ncdf_cloud_mask]


admin.site.register(DataCube, OpenEODataCubeAdmin)
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



