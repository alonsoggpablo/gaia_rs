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
class OpenEOCollection(models.Model):
    collection_id = models.CharField(max_length=100, unique=True)
    bands=models.JSONField()

    def __str__(self):
        return self.collection_id

class OpenEOCalculation(models.Model):
    collection = models.ForeignKey(OpenEOCollection, on_delete=models.CASCADE)
    calculation=models.CharField(max_length=100)
    result=models.JSONField()
    def __str__(self):
        return self.calculation


class OpenEODataCube(models.Model):
    calculation=models.ForeignKey(OpenEOCalculation, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    spatial_extent = models.PolygonField()  # Store the spatial extent as a polygon
    temporal_extent_start = models.DateTimeField()
    temporal_extent_end = models.DateTimeField()
    bands=models.JSONField()
    max_cloud_cover=models.FloatField()
    properties = models.JSONField()
    north= models.FloatField()
    south= models.FloatField()
    east= models.FloatField()
    west= models.FloatField()
    image= models.ImageField(upload_to='images/', null=True, blank=True)
    def save(self, *args, **kwargs):
        self.north=self.spatial_extent.envelope[0][2][1]
        self.south=self.spatial_extent.envelope[0][0][1]
        self.east=self.spatial_extent.envelope[0][1][0]
        self.west=self.spatial_extent.envelope[0][0][0]
        self.bands=self.calculation.collection.bands
        super(OpenEODataCube, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def process(self):
        connection=openeo.connect('openeo.dataspace.copernicus.eu')
        connection.authenticate_oidc()
        datacube=connection.load_collection(
            self.collection.collection_id,
            bands=self.bands,
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
