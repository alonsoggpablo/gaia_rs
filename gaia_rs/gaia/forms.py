import json

from django import forms
from django.contrib.gis.forms import PolygonField, OSMWidget
from django.utils.safestring import mark_safe
from .models import DataCube

class CustomSpatialExtentWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        # Customize the HTML markup here
        html = '''
        <head>
      <style>
        .map-container {
            width: 100%;
            height: 600px; /* Adjust the height as needed */
        }
    
    </style>
    </head>
<body>
    <div  class="map-container" id="map"></div>
    <textarea id="id_spatial_extent" class="vSerializedField required" cols="150" rows="10" name="spatial_extent" hidden></textarea>
    <script>
        var map = L.map('map').setView([40.4166, -3.7038400], 6);

        // Add various layers using leaflet-providersESP
         var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib })

        var pnoa= L.tileLayer.providerESP('PNOA').addTo(map);
        var ngeo=L.tileLayer.providerESP('NombresGeograficos').addTo(map);
        var pnoa_ngeo=L.layerGroup([pnoa,ngeo]);

        var control=L.control.layers({
        'OSM': osm.addTo(map),
        'PNOA': pnoa.addTo(map),
        'PNOA-NGEO': pnoa_ngeo.addTo(map)
        })
        control.addTo(map);
        
         // Initialize the Leaflet Draw control
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems,
            edit: false,
            remove: true,
            poly: {
                allowIntersection: false
            }
        },
        draw: {
            polygon: {
                allowIntersection: false,
                showArea: true
            }
        }
    });
    map.addControl(drawControl);  
    map.on(L.Draw.Event.CREATED, function (event) {
        var layer = event.layer;
 // Extract coordinates and display in the textarea
        var coordinates = layer.toGeoJSON().geometry.coordinates;
        var geojsonPolygon = {type: 'Polygon',coordinates: coordinates};
        document.getElementById('id_spatial_extent').value = JSON.stringify(geojsonPolygon);
        drawnItems.addLayer(layer);
        
    });
    </script>
    </body>
    </html>
</div>'''
        return mark_safe(html)
class DataCubeForm(forms.ModelForm):
    spatial_extent=PolygonField(widget=CustomSpatialExtentWidget)
    class Meta:
        model= DataCube
        fields=['name','temporal_extent_start','temporal_extent_end','max_cloud_cover','dataproduct','spatial_extent']
        widgets={
                'spatial_extent':OSMWidget(),
                 'temporal_extent_end': forms.DateInput(attrs={'type': 'date'}),
                 'temporal_extent_start':forms.DateInput(attrs={'type':'date'}),
                 }
        #     'spatial_extent':OSMWidget(attrs={
        #     'map_width': 800,  # Set the width of the map in pixels
        #     'map_height': 600,  # Set the height of the map in pixels
        #     'default_lon': -3.70384,  # Set the default longitude
        #     'default_lat': 40.4166,  # Set the default latitude
        #     'default_zoom': 6,
        #     }),
        #     'temporal_extent_end':forms.DateInput(attrs={'type':'date'}),
        #     'temporal_extent_start':forms.DateInput(attrs={'type':'date'}),
        # }
    def clean(self):
        cleaned_data=super().clean()
        temporal_extent_start=cleaned_data.get("temporal_extent_start")
        temporal_extent_end=cleaned_data.get("temporal_extent_end")
        if temporal_extent_start > temporal_extent_end:
            raise forms.ValidationError("Temporal extent start must be before temporal extent end")
        return cleaned_data
class EditDataCubeForm(forms.ModelForm):
    class Meta:
        model= DataCube
        fields=['name','temporal_extent_start','temporal_extent_end','max_cloud_cover','dataproduct','spatial_extent']
        widgets={
                'spatial_extent':OSMWidget(),
                 'temporal_extent_end': forms.DateInput(attrs={'type': 'date'}),
                 'temporal_extent_start':forms.DateInput(attrs={'type':'date'}),
                 }

    def clean(self):
        cleaned_data=super().clean()
        temporal_extent_start=cleaned_data.get("temporal_extent_start")
        temporal_extent_end=cleaned_data.get("temporal_extent_end")
        if temporal_extent_start > temporal_extent_end:
            raise forms.ValidationError("Temporal extent start must be before temporal extent end")
        return cleaned_data



