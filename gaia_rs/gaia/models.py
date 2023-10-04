import datetime
import json
import os
import time
from io import BytesIO
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import openeo
import pandas as pd
import rasterio
import shapely
import xarray as xr
from celery.signals import task_success, task_prerun
from django.contrib.gis.db import models
from django.core.files import File
from rasterio.transform import from_origin

from .tasks import download_copernicus_results, run_batch_job_process_datacube


def remove_brackets(value):
    try:
        return value[0][0]
    except:
        return value

def generate_timeseries_plot(self,df,param):
    plt.title(param+ '_' + self.name)
    plt.xlabel('Date')
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
    plt.xticks(rotation=90)
    plt.grid(True)
    df[param].plot(marker='o', color='green', linestyle='-', figsize=(20, 10))
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    self.plot_image.save(param+'.png', File(buffer), save=False)
    # self.timeseries=df.to_dict(orient='split')
    self.save()

def generate_raster_1band(self,ds,xarray,param):

    for t in range(0, ds.dims['t']):
        date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
        west = self.west
        east = self.east
        north = self.north
        south = self.south
        name = self.name.lower()
        lon_resolution=(east-west)/ds.dims['x']
        lat_resolution=(north-south)/ds.dims['y']
        transform= from_origin(west, north, lon_resolution, lat_resolution)
        output_geotiff = f'{name}_{param}_{date}.tif'.replace('-', '_')
        data = xarray.isel(t=t)
        clipped_data=np.clip(data,0,1)
        intensity_map=np.nan_to_num(clipped_data,nan=0)
        crs='+proj=latlong'
        with rasterio.open(output_geotiff, 'w', driver='GTiff', height=data.sizes['y'], width=data.sizes['x'],
                           count=1, dtype=str(intensity_map.dtype), crs=crs, transform=transform) as dst:
            dst.write(intensity_map, 1)

        geoimage_instance = GeoImage(name=output_geotiff,
                                     processing_date=datetime.datetime.now(),
                                     observation_date=date,
                                     datacube=self)

        with open(output_geotiff, 'rb') as raster_file:
            geoimage_instance.raster_file.save(output_geotiff, File(raster_file))

        geoimage_instance.save()
        os.remove(output_geotiff)

def generate_raster_3band(self,ds,param):

    for t in range(0, ds.dims['t']):
        date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
        west = self.west
        east = self.east
        north = self.north
        south = self.south
        name = self.name.lower()
        lon_resolution=(east-west)/ds.dims['x']
        lat_resolution=(north-south)/ds.dims['y']
        transform= from_origin(west, north, lon_resolution, lat_resolution)
        red = ds.isel(t=t)['B04']
        green = ds.isel(t=t)['B03']
        blue = ds.isel(t=t)['B02']
        # Normalize the bands to the range [0, 1]
        normalized_red = (red - red.min()) / (red.max() - red.min())
        normalized_green = (green - green.min()) / (green.max() - green.min())
        normalized_blue = (blue - blue.min()) / (blue.max() - blue.min())

        output_geotiff = f'{name}_{param}_{date}.tif'.replace('-', '_')
        rgb_array=np.stack([normalized_red, normalized_green, normalized_blue], axis=0)
        crs='+proj=latlong'
        with rasterio.open(output_geotiff, 'w', driver='GTiff', height=red.sizes['y'], width=red.sizes['x'],
                           count=3, dtype=str(rgb_array.dtype), crs=crs, transform=transform) as dst:
            dst.write(rgb_array, [1,2,3])

        geoimage_instance = GeoImage(name=output_geotiff,
                                     processing_date=datetime.datetime.now(),
                                     observation_date=date,
                                     datacube=self)

        with open(output_geotiff, 'rb') as raster_file:
            geoimage_instance.raster_file.save(output_geotiff, File(raster_file))

        geoimage_instance.save()

        os.remove(output_geotiff)

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField("Population 2005")
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField("2 Digit ISO", max_length=2)
    iso3 = models.CharField("3 Digit ISO", max_length=3)
    un = models.IntegerField("United Nations Code")
    region = models.IntegerField("Region Code")
    subregion = models.IntegerField("Sub-Region Code")
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name
class Band(models.Model):
    name = models.CharField(max_length=100)
    description = models.JSONField()
    collection = models.CharField(max_length=100)

    def __str__(self):
        description_text=""
        if 'common_name' in self.description:
            description_text=self.description['common_name']
        if 'description' in self.description:
            description_text=description_text+"_"+self.description['description']
        return self.collection+"_"+self.name+"_"+description_text
class Category(models.Model):
    category=models.CharField(max_length=100)
    def __str__(self):
        return self.category
class Script(models.Model):
    script=models.CharField(max_length=100)
    description=models.TextField()
    def __str__(self):
        return self.script
class DataProduct(models.Model):
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    script=models.ForeignKey(Script, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.TextField()
    bands = models.ManyToManyField(Band)
    def __str__(self):
        return self.category.category+'_'+self.name
    class Meta:
        ordering = ['category__category', 'name']

class DataCube(models.Model):
    name = models.CharField(max_length=100)
    spatial_extent = models.PolygonField()  # Store the spatial extent as a polygon
    temporal_extent_start = models.DateTimeField()
    temporal_extent_end = models.DateTimeField()
    dataproduct=models.ForeignKey(DataProduct, on_delete=models.CASCADE)
    bands=models.JSONField()
    max_cloud_cover=models.FloatField(default=85)
    north= models.FloatField(default=0)
    south= models.FloatField(default=0)
    east= models.FloatField(default=0)
    west= models.FloatField(default=0)
    ncdfile=models.FileField(upload_to='ncdf/', null=True, blank=True)
    timeseries=models.JSONField(null=True, blank=True)
    plot_image=models.ImageField(upload_to='plot_images/', null=True, blank=True)
    status=models.CharField(max_length=100, default='created')


    def save(self, *args, **kwargs):
            self.north=self.spatial_extent.envelope[0][2][1]
            self.south=self.spatial_extent.envelope[0][0][1]
            self.east=self.spatial_extent.envelope[0][1][0]
            self.west=self.spatial_extent.envelope[0][0][0]
            self.bands=list(self.dataproduct.bands.values_list('name', flat=True))
            super(DataCube, self).save(*args, **kwargs)
    def get_ncdf(self):
        self.status='processing'
        self.save()
        cube_dict={
            'collection':self.dataproduct.bands.first().collection,
            'bands':list(self.dataproduct.bands.all().values_list('name', flat=True)),
            'temporal_extent':(self.temporal_extent_start, self.temporal_extent_end),
            'spatial_extent':{'west': self.west, 'east': self.east, 'north': self.north, 'south': self.south},
            'max_cloud_cover':self.max_cloud_cover,
            'category':self.dataproduct.category.category,
        }


        run_batch_job_process_datacube.delay(cube_dict,self.id)





    def get_ndvi(self):
        ds = xr.open_dataset(self.ncdfile.path)

        # Select bands (NIR and Red) for NDVI calculation
        nir = ds['B08']
        red = ds['B04']
        # Calculate NDVI
        xarray = (nir - red) / (nir + red)
        df = pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['ndvi'] = (df['B08'] - df['B04']) / (df['B04'] + df['B08'])
        generate_timeseries_plot(self,df,'ndvi')
        generate_raster_1band(self,ds,xarray,'ndvi')
    def get_rgb(self):
        ds = xr.open_dataset(self.ncdfile.path)

        generate_raster_3band(self,ds,'rgb')
    def get_bsi(self):
        ds = xr.open_dataset(self.ncdfile.path)

        # Select bands for BSI calculation
        b08 = ds['B08']
        b04 = ds['B04']
        b02 = ds['B02']
        b11 = ds['B11']

        # Calculate BSI
        xarray=((b11+b04)-(b08+b02))/((b11+b04)+(b08+b02))
        df = pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['bsi'] = ((df['B11'] + df['B04'])-(df['B08']+df['B02'])) / ((df['B11'] + df['B04'])+(df['B08']+df['B02']))
        generate_timeseries_plot(self, df, 'bsi')
        generate_raster_1band(self,ds,xarray,'bsi')
    def get_ndci(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b05= ds['B05']
        b04= ds['B04']
        ndci=(b05-b04)/(b05+b04)
        df = pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['ndci'] = (df['B05'] - df['B04'])/ (df['B05'] + df['B04'])
        generate_timeseries_plot(self, df, 'ndci')
        generate_raster_1band(self,ds,ndci,'ndci')
    def get_msi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b08= ds['B08']
        b11= ds['B11']
        msi=b11/b08
        df = pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['msi'] = df['B11']/ df['B08']
        generate_timeseries_plot(self, df, 'msi')
        generate_raster_1band(self,ds,msi,'msi')
    def get_evi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b08= ds['B08']
        b04= ds['B04']
        b02= ds['B02']
        evi=2.5*((b08-b04)/(b08+6*b04-7.5*b02+1))
        df = pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['evi'] = 2.5*(df['B08'] - df['B04'])/ (df['B08'] + 6*df['B04']-7.5*df['B02']+1)
        generate_timeseries_plot(self, df, 'evi')
        generate_raster_1band(self,ds,evi,'evi')
    def get_ndsi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b03= ds['B03']
        b11= ds['B11']
        ndsi=(b03-b11)/(b03+b11)
        generate_raster_1band(self,ds,ndsi,'ndsi')
        df= pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['ndsi'] = (df['B03'] - df['B11'])/ (df['B03'] + df['B11'])
        generate_timeseries_plot(self, df, 'ndsi')
    def get_ndwi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b03= ds['B03']
        b08= ds['B08']
        ndwi=(b03-b08)/(b03+b08)
        generate_raster_1band(self,ds,ndwi,'ndwi')
        df= pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['ndwi'] = (df['B03'] - df['B08'])/ (df['B03'] + df['B08'])
        generate_timeseries_plot(self, df, 'ndwi')
    def get_bais(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b04= ds['B04']
        b06= ds['B06']
        b12= ds['B12']
        b8A= ds['B8A']
        b07= ds['B07']

        bais=(1-((b06*b07*b8A)/b04)**0.5)*((b12-b8A)/((b12+b8A)**0.5)+1)
        generate_raster_1band(self,ds,bais,'bais')
        df= pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['bais'] = (1-((df['B06']*df['B07']*df['B8A'])/df['B04'])**0.5)*((df['B12']-df['B8A'])/((df['B12']+df['B8A'])**0.5)+1)
        generate_timeseries_plot(self, df, 'bais')
    def get_apa(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b02= ds['B02']
        b03= ds['B03']
        b04= ds['B04']
        b05= ds['B05']
        b08= ds['B08']
        b8A= ds['B8A']
        b11= ds['B11']

        moisture=(b08-b11)/(b08+b11)
        ndwi=(b03-b08)/(b03+b08)
        water_bodies=(ndwi-moisture)/(ndwi+moisture)
        water_plants=(b05-b04)/(b05+b04)
        ndgr=b03/b04
        nir2=b04+(b11-b04)*((832.8 - 664.6) / (1613.7 - 664.6))
        fai=b08-nir2
        bratio=(b03-0.175)/(0.39-0.175)
        generate_raster_1band(self,ds,water_plants,'water_plants')
        generate_raster_1band(self,ds,water_bodies,'water_bodies')
        generate_raster_1band(self,ds,moisture,'moisture')
        generate_raster_3band(self,ds,'rgb')
    def get_ndyi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b02= ds['B02']
        b03= ds['B03']
        ndyi=(b03-b02)/(b03+b02)
        generate_raster_1band(self,ds,ndyi,'ndyi')
        df= pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['ndyi'] = (df['B03'] - df['B02'])/ (df['B03'] + df['B02'])
        generate_timeseries_plot(self, df, 'ndyi')
    def sar_rvi(self):
        ds = xr.open_dataset(self.ncdfile.path)
        VV= ds['VV']
        VH= ds['VH']
        rvi=(4*VH)/(VV+VH)
        generate_raster_1band(self,ds,rvi,'rvi')
        df=pd.DataFrame.from_dict(self.timeseries).applymap(remove_brackets)
        df['rvi'] = (4*df['VH'])/(df['VV']+df['VH'])
        generate_timeseries_plot(self, df, 'rvi')


    def __str__(self):
        return self.name
class GeoImage(models.Model):
    datacube=models.ForeignKey(DataCube, on_delete=models.CASCADE, related_name='geoimages')
    name=models.CharField(max_length=100)
    processing_date=models.DateTimeField(auto_now_add=True)
    observation_date=models.DateField(null=True,blank=True)
    raster_file=models.FileField(upload_to='raster_files',blank=True, null=True)

    def __str__(self):
        return self.name

class MapLayer(models.Model):
    name=models.CharField(max_length=100)
    attribution=models.CharField(max_length=100)
    description=models.TextField()
    url=models.URLField()
    def __str__(self):
        return self.name



@task_success.connect(sender=download_copernicus_results)
def download_copernicus_task_success_handler(sender, result, **kwargs):
    print("Datacube process was successful!")
    datacube=DataCube.objects.get(pk=result)
    datacube.status='saving file'
    datacube.save()
    with open('openEO.nc', 'rb') as f:
         ncdfile = File(f)
         datacube.ncdfile.save('openEO.nc', ncdfile)


    # datacube.timeseries={}
    # for band in list(datacube.dataproduct.bands.all().values_list('name', flat=True)):
    #     cube.band(band).aggregate_spatial(geometries=geopandas.GeoSeries([shapely.geometry.Polygon(cube.spatial_extent.coords[0])]).__geo_interface__, reducer='mean').download('timeseries_'+band+'.json')
    #     with open('timeseries_'+band+'.json') as f:
    #         datacube.timeseries.update({band:json.load(f)})
    #         datacube.save()
    #         os.remove('timeseries_'+band+'.json')
