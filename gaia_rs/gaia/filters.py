

from django_filters import FilterSet
from .models import DataCube


class DataCubeFilter(FilterSet):
    class Meta:
        model = DataCube
        fields = {'dataproduct':['exact']}

