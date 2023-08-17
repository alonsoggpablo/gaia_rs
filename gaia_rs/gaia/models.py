import json
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
                except:pass


            super(DataCube, self).save(*args, **kwargs)

    def get_ndvi(self):
        ds = xr.open_dataset(self.ncdfile.path)

        # Select bands (NIR and Red) for NDVI calculation
        nir = ds['B08']
        red = ds['B04']

        # Calculate NDVI
        ndvi = (nir - red) / (nir + red)

        # Plot NDVI intensity map
        for t in range(0, ds.dims['t']):
            date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
            plt.figure(figsize=(10, 8))
            plt.imshow(ndvi.isel(t=t), cmap='RdYlGn', vmin=-1, vmax=1)  # Adjust colormap and limits
            plt.colorbar(label='NDVI')
            plt.title(f'NDVI Intensity Map  - {date}')
            # Render the plot to an in-memory PNG image
            canvas = FigureCanvasAgg(plt.gcf())
            canvas.draw()
            # Extract pixel data as a numpy array
            width, height = canvas.get_width_height()
            pixel_data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8).reshape((height, width, 3))
            # Create GeoTIFF dataset
            driver = gdal.GetDriverByName('GTiff')
            output_geotiff = f'ndvi_{date}.tif'.replace('-', '_')
            out_ds = driver.Create(output_geotiff, width, height, 3, gdal.GDT_Byte)

            # Write RGB data to bands
            for i in range(3):
                out_ds.GetRasterBand(i + 1).WriteArray(pixel_data[:, :, i])

            # Set geotransform and projection
            geotransform = (-10, 20 / width, 0, 10, 0, -20 / height)
            out_ds.SetGeoTransform(geotransform)

            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)  # Set the coordinate system (EPSG:4326 = WGS84)
            out_ds.SetProjection(srs.ExportToWkt())
            # Save and close the GeoTIFF dataset
            out_ds = None

            geoimage_instance=GeoImage(name=output_geotiff,
                                       processing_date=datetime.datetime.now(),
                                       observation_date=date,
                                       datacube=self)

            with open(output_geotiff, 'rb') as raster_file:
                geoimage_instance.raster_file.save(output_geotiff, File(raster_file))

            geoimage_instance.save()


    def __str__(self):
        return self.name
class GeoImage(models.Model):
    datacube=models.ForeignKey(DataCube, on_delete=models.CASCADE, related_name='geoimages')
    name=models.CharField(max_length=100)
    processing_date=models.DateTimeField(auto_now_add=True)
    observation_date=models.DateField()
    raster_file=models.FileField(upload_to='raster_files',blank=True, null=True)

    def __str__(self):
        return self.name



