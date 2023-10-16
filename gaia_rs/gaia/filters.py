

from django_filters import FilterSet, ModelChoiceFilter
from .models import DataCube, DataProduct, Category


class DataCubeFilter(FilterSet):
    class Meta:
        model = DataCube
        fields = {'dataproduct':['exact']}


class DataProductFilter(FilterSet):
    class Meta:
        model = DataProduct
        fields = {'category':['exact']}
    def get_categories():
        dataproducts=DataProduct.objects.all()
        categories=[]
        for dataproduct in dataproducts:
            categories.append(dataproduct.category)
        return categories

    category=ModelChoiceFilter(queryset=Category.objects.filter(category__in=get_categories()).order_by('category').distinct())