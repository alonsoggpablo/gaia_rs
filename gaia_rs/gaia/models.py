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


class Square(models.Model):
    name = models.CharField(max_length=100)
    geom = models.MultiPolygonField()
    north= models.FloatField()
    south= models.FloatField()
    east= models.FloatField()
    west= models.FloatField()
    def save(self, *args, **kwargs):
        self.north=self.geom.envelope[0][2][1]
        self.south=self.geom.envelope[0][0][1]
        self.east=self.geom.envelope[0][1][0]
        self.west=self.geom.envelope[0][0][0]
        super(Square, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
