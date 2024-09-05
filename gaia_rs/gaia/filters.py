

from django_filters import FilterSet, ModelChoiceFilter
from .models import DataCube, DataProduct, Category
from django.db.utils import OperationalError


class DataCubeFilter(FilterSet):
    class Meta:
        model = DataCube
        fields = {'dataproduct': ['exact']}


class DataProductFilter(FilterSet):
    def get_categories():
        dataproducts = []
        try:
            dataproducts = DataProduct.objects.all()
        except: return[]
        categories = []
        try:
            for dataproduct in dataproducts:
                categories.append(dataproduct.category)
        except:pass
        return categories

    category = ModelChoiceFilter(queryset=Category.objects.filter(
        category__in=get_categories()).order_by('category').distinct())

    class Meta:
        model = DataProduct
        fields = {'category': ['exact']}