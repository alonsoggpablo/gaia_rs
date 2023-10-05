import django_tables2 as tables
from django.urls import reverse


from .models import DataCube, GeoImage
from .views import *


class DataCubeTable(tables.Table):

    name=tables.LinkColumn(
        'gaia:datacube_detail',
        args=[tables.A('pk')],
        text=lambda record: record.name,
    )

    edit = tables.TemplateColumn(template_name='edit_datacube_button.html', verbose_name='Edit', orderable=False)
    delete=tables.TemplateColumn(template_name='delete_datacube_button.html',verbose_name='Delete',orderable=False)

    class Meta:
        model = DataCube
        fields=('name','dataproduct')
        template_name = 'django_tables2/bootstrap4.html'
        order_by = 'name'

class DataCubeDetailTable(tables.Table):

    process_datacube = tables.TemplateColumn(
        template_name='process_datacube_button.html',
        verbose_name='Process',
        orderable=False,# Optional: Customize the column header
    )

    status=tables.TemplateColumn(
        template_name ='status.html',
        verbose_name='Status',  # Optional: Customize the column header
    )

    edit=tables.TemplateColumn(template_name='edit_datacube_button.html',verbose_name='Edit',orderable=False)
    delete=tables.TemplateColumn(template_name='delete_datacube_button.html',verbose_name='Delete',orderable=False)

    class Meta:
        model = DataCube
        fields=('name','dataproduct','temporal_extent_start','temporal_extent_end','max_cloud_cover','status')
        template_name = 'django_tables2/bootstrap4.html'



class GeoImageTable(tables.Table):
    raster_file=tables.LinkColumn(
        'gaia:raster_file',
        args=[tables.A('pk')],
        text=lambda record: record.name,
    )

    delete=tables.TemplateColumn(template_name='delete_geoimage_button.html',verbose_name='Delete',orderable=False)
    class Meta:
        model = GeoImage
        fields=('name','processing_date','observation_date','raster_file')
        template_name = 'django_tables2/bootstrap4.html'

    def __init__(self,queryset=None,*args,**kwargs):
        queryset=GeoImage.objects.filter(datacube=kwargs.pop('datacube'))
        super().__init__(queryset,*args,**kwargs)