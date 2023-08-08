from django.shortcuts import render

# Create your views here.

from django.contrib.gis.geos import MultiPolygon, Polygon, LinearRing, Point
from models import Square


def create_square(name,latitude_north, latitude_south, longitude_east, longitude_west):
    longitude_center=(longitude_east+longitude_west)/2
    latitude_center=(latitude_north+latitude_south)/2
    # Define the coordinates of the square's corners
    north = Point(y=latitude_north, x=longitude_center)
    south = Point(y=latitude_south, x=longitude_center)
    east = Point(y=latitude_center, x=longitude_east)
    west = Point(y=latitude_center, x=longitude_west)

    # Create a LinearRing for the square
    ring = LinearRing([north, east, south, west, north])

    # Create a Polygon from the LinearRing
    polygon = Polygon(ring)

    # Create a MultiPolygon from the Polygon
    multi_polygon = MultiPolygon(polygon)

    # Create a Square instance
    square = Square(name=name, geom=multi_polygon)
    square.save()

create_square( 'test',51.204641,51.189474,3.254708,3.202609)