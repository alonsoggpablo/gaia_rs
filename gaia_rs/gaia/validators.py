from django.db import models
from django.core.exceptions import ValidationError

def validate_polygon_area(value):
    # Replace 'max_area' with your desired maximum area in square units
    max_area = 0.1  # Adjust this value as needed

    # Calculate the area of the polygon using a suitable method
    # This depends on the units used by your PolygonField, adjust accordingly
    area = value.area

    if area > max_area:
        raise ValidationError(f"Polygon area exceeds the maximum allowed area ({1000*max_area} square kilometer).")


