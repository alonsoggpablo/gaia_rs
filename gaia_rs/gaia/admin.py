from django.contrib.gis import admin

# Register your models here.

from .models import WorldBorder, OpenEOCollection, OpenEODataCube, OpenEOCalculation

admin.site.register(WorldBorder,admin.GISModelAdmin)

admin.site.register(OpenEOCollection, admin.GISModelAdmin)

def process_datacube(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.process()

class OpenEODataCubeAdmin(admin.GISModelAdmin):
    list_display = ('calculation', 'name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    actions = [process_datacube]

admin.site.register(OpenEODataCube, OpenEODataCubeAdmin)

admin.site.register(OpenEOCalculation, admin.GISModelAdmin)
