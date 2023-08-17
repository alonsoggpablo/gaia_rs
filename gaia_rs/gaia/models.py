import json

import openeo
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
    image= models.ImageField(upload_to='images/', null=True, blank=True)
    ncdfile=models.FileField(upload_to='ncdf/', null=True, blank=True)
    def save(self, *args, **kwargs):
            self.north=self.spatial_extent.envelope[0][2][1]
            self.south=self.spatial_extent.envelope[0][0][1]
            self.east=self.spatial_extent.envelope[0][1][0]
            self.west=self.spatial_extent.envelope[0][0][0]
            self.bands=list(self.dataproduct.bands.values_list('name', flat=True))
            super(DataCube, self).save(*args, **kwargs)
    def load_ncdf(self):
    def __str__(self):
        return self.name
    def get_tiff(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.dataproduct.bands.first().collection,
            bands=list(self.dataproduct.bands.all().values_list('name',flat=True)),
            temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
            spatial_extent={'west':self.west,'east':self.east, 'north':self.north, 'south':self.south},
            max_cloud_cover=self.max_cloud_cover,
        )
        datacube = datacube.max_time()
        job = datacube.execute_batch()

        print(job.job_id)
        print(job.status())

        results = job.get_results()
        results.download_files()
        with open('openEO.tif', 'rb') as f:
            image_file=File(f)
            self.image.save('openEO.tif', image_file)
        self.save()
    def get_ncdf(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.dataproduct.bands.first().collection,
            bands=list(self.dataproduct.bands.all().values_list('name',flat=True)),
            temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
            spatial_extent={'west':self.west,'east':self.east, 'north':self.north, 'south':self.south},
            max_cloud_cover=self.max_cloud_cover,
        )

        datacube.download("openEO.nc")

        with open('openEO.nc', 'rb') as f:
            ncdfile=File(f)
            self.ncdfile.save('openEO.nc', ncdfile)
        self.save()
    def get_ncdf_without_max_cloud_cover(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.dataproduct.bands.first().collection,
            bands=list(self.dataproduct.bands.all().values_list('name',flat=True)),
            temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
            spatial_extent={'west':self.west,'east':self.east, 'north':self.north, 'south':self.south},
        )

        datacube.download("openEO.nc")
        with open('openEO.nc', 'rb') as f:
            ncdfile=File(f)
            self.ncdfile.save('openEO.nc', ncdfile)
        self.save()
    def get_ncdf_cloud_mask(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.dataproduct.bands.first().collection,
            bands=list(self.dataproduct.bands.all().values_list('name',flat=True)),
            temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
            spatial_extent={'west':self.west,'east':self.east, 'north':self.north, 'south':self.south},
            max_cloud_cover=self.max_cloud_cover,
        )
        scl_band=datacube.band('SCL')
        cloud_mask=(scl_band==3)|(scl_band==8)|(scl_band==9)
        cloud_mask = cloud_mask.resample_cube_spatial(datacube)
        cube_masked = datacube.mask(cloud_mask)
        composite_masked = cube_masked.max_time()
        composite_masked.download("openEO.nc")
        with open('openEO.nc', 'rb') as f:
            ncdfile=File(f)
            self.ncdfile.save('openEO.nc', ncdfile)
        self.save()
    def get_evi(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.dataproduct.bands.first().collection,
            bands=list(self.dataproduct.bands.all().values_list('name',flat=True)),
            temporal_extent=(self.temporal_extent_start, self.temporal_extent_end),
            spatial_extent={'west':self.west,'east':self.east, 'north':self.north, 'south':self.south},
            max_cloud_cover=self.max_cloud_cover,
        )

        blue=datacube.band('B02')*0.0001
        red=datacube.band('B04')*0.0001
        nir=datacube.band('B08')*0.0001
        evi_cube=(2.5*(nir-red))/(nir+6*red-7.5*blue+1)
        scl_band=datacube.band('SCL')
        mask=(scl_band!=4)
        mask_resampled=mask.resample_cube_spatial(evi_cube)
        evi_cube_masked=evi_cube.mask(mask_resampled)
        evi_composite=evi_cube_masked.max_time()
        job = evi_composite.execute_batch()

        print(job.job_id)
        print(job.status())

        results = job.get_results()
        results.download_files()
        with open('openEO.tif', 'rb') as f:
            image_file=File(f)
            self.image.save('openEO.tif', image_file)
        self.save()


