from django.contrib.gis import admin

# Register your models here.

from .models import WorldBorder, DataCube, Band, DataProduct

admin.site.register(WorldBorder,admin.GISModelAdmin)


def process_datacube(modeladmin, request, queryset):
    for datacube in queryset:
        datacube.process()

class OpenEODataCubeAdmin(admin.GISModelAdmin):
    exclude = ('bands','job_results')
    list_display = ('name', 'temporal_extent_start', 'temporal_extent_end', 'max_cloud_cover')
    actions = [process_datacube]


admin.site.register(DataCube, OpenEODataCubeAdmin)
class BandAdmin(admin.GISModelAdmin):
    list_display = ('name', 'description','collection')
    list_filter = ('collection',)
    ordering = ('collection','name',)

admin.site.register(Band,BandAdmin)

admin.site.register(DataProduct,admin.GISModelAdmin)

