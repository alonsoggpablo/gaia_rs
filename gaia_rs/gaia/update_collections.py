import requests
from gaia.models import OpenEOCollection
import openeo

def fetch_and_store_collections():
    connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
    connection.authenticate_oidc()
    collections=connection.list_collection_ids()
    for collection in collections:
        OpenEOCollection.objects.get_or_create(
                        collection_id=collection,
                        bands=connection.describe_collection(collection)['cube:dimensions']['bands']['values'],
                     )


fetch_and_store_collections()

