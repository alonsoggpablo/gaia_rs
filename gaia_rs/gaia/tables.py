import django_tables2 as tables
from django.urls import reverse
from .models import DataCube, GeoImage


class DataCubeTable(tables.Table):

    name=tables.LinkColumn(
        'gaia:datacube_detail',
        args=[tables.A('pk')],
        text=lambda record: record.name,
    )
    class Meta:
        model = DataCube
        fields=('name','dataproduct')
        template_name = 'django_tables2/bootstrap4.html'

class DataCubeDetailTable(tables.Table):

    process_datacube = tables.TemplateColumn(
        template_name='process_datacube_button.html',
        verbose_name='Process Datacube',  # Optional: Customize the column header
    )
    class Meta:
        model = DataCube
        fields=('name','dataproduct','temporal_extent_start','temporal_extent_end','max_cloud_cover')
        template_name = 'django_tables2/bootstrap4.html'

class GeoImageTable(tables.Table):
    raster_file=tables.LinkColumn(
        'gaia:raster_file',
        args=[tables.A('pk')],
        text=lambda record: record.name,
    )
    class Meta:
        model = GeoImage
        fields=('name','processing_date','observation_date','raster_file')
        template_name = 'django_tables2/bootstrap4.html'

    def __init__(self,queryset=None,*args,**kwargs):
        queryset=GeoImage.objects.filter(datacube=kwargs.pop('datacube'))
        super().__init__(queryset,*args,**kwargs)