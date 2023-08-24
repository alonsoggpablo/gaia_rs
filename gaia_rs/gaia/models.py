import json
import rasterio
from rasterio.plot import show
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
from rasterio.enums import ColorInterp
from rasterio.transform import from_origin
import cv2
import matplotlib.pyplot as plt
import datetime
from pathlib import Path
from django.contrib.gis.gdal import GDALRaster
from osgeo import gdal, osr
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
import xarray as xr
import openeo
from django.contrib.gis.geos import Point
from django.core.files import File
from django.db import models
from django.contrib.gis.db import models
from PIL import Image
from skimage import exposure
import cartopy.crs as ccrs
import urllib.request

def generate_raster_1band(self,ds,xarray,param):

    for t in range(0, ds.dims['t']):
        date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
        west = self.west
        east = self.east
        north = self.north
        south = self.south
        lon_resolution=(east-west)/ds.dims['x']
        lat_resolution=(north-south)/ds.dims['y']
        transform= from_origin(west, north, lon_resolution, lat_resolution)
        output_geotiff = f'{param}_{date}.tif'.replace('-', '_')
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
def generate_raster_3band(self,ds,param):

    for t in range(0, ds.dims['t']):
        date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
        west = self.west
        east = self.east
        north = self.north
        south = self.south
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

        output_geotiff = f'{param}_{date}.tif'.replace('-', '_')
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
    revisit_time=models.IntegerField(default=1)
    spatial_resolution=models.IntegerField(default=10)
    def __str__(self):
        return self.name
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

    def save(self, *args, **kwargs):
            self.north=self.spatial_extent.envelope[0][2][1]
            self.south=self.spatial_extent.envelope[0][0][1]
            self.east=self.spatial_extent.envelope[0][1][0]
            self.west=self.spatial_extent.envelope[0][0][0]
            self.bands=list(self.dataproduct.bands.values_list('name', flat=True))
            super(DataCube, self).save(*args, **kwargs)
    def get_ncdf(self):
        connection = openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        try:
            datacube = connection.load_collection(
                self.dataproduct.bands.first().collection,
                bands=list(self.dataproduct.bands.all().values_list('name', flat=True)),
                temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
                spatial_extent={'west': self.west, 'east': self.east, 'north': self.north, 'south': self.south},
                max_cloud_cover=self.max_cloud_cover,
            )

            datacube.download("openEO.nc")
            with open('openEO.nc', 'rb') as f:
                ncdfile = File(f)
                self.ncdfile.save('openEO.nc', ncdfile)
        except:
            try:
                datacube = connection.load_collection(
                    self.dataproduct.bands.first().collection,
                    bands=list(self.dataproduct.bands.all().values_list('name', flat=True)),
                    temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
                    spatial_extent={'west': self.west, 'east': self.east, 'north': self.north, 'south': self.south},
                )

                datacube.download("openEO.nc")
                with open('openEO.nc', 'rb') as f:
                    ncdfile = File(f)
                    self.ncdfile.save('openEO.nc', ncdfile)
            except:
                pass
    def get_ndvi(self):
        ds = xr.open_dataset(self.ncdfile.path)

        # Select bands (NIR and Red) for NDVI calculation
        nir = ds['B08']
        red = ds['B04']

        # Calculate NDVI
        xarray = (nir - red) / (nir + red)

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

        generate_raster_1band(self,ds,xarray,'bsi')
    def get_ndci(self):
        ds = xr.open_dataset(self.ncdfile.path)
        b05= ds['B05']
        b04= ds['B04']
        ndci=(b05-b04)/(b05+b04)
        generate_raster_1band(self,ds,ndci,'ndci')


    #TODO: add get method for all dataproducts. Reconsider scripts field in dataproduct.

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



