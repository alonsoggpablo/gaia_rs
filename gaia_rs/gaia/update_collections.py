import requests
from gaia.models import Band
import openeo



def fetch_and_store_collections():
    connection = openeo.connect(url="openeo.dataspace.copernicus.eu")
    connection.authenticate_oidc()
    collections=connection.list_collection_ids()
    for collection in collections:
        i=0
        for band in connection.describe_collection(collection)['cube:dimensions']['bands']['values']:
            Band.objects.get_or_create(name=band,
                                       collection=collection,
                                       description=connection.describe_collection(collection)['summaries']['eo:bands'][i])
            i=i+1
fetch_and_store_collections()

