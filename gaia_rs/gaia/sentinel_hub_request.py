import json

import pandas as pd
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session



# Your client credentials
client_id = 'sh-32126578-7fe0-4934-a5f0-b900b7c3293f'
client_secret = 'VfQ8onCctNt72piUu44HLQfR4v5qo5vB'

# Create a session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

# Get token for the session
token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                          client_secret=client_secret)

evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["VV"],
    output: { id: "default", bands: 1, sampleType: SampleType.FLOAT32 },
  }
}

function evaluatePixel(samples) {
  return [samples.VV]
}
"""

north=41.415843680127004
south=41.20886048278024
east=-4.515979965182463
west=-5.005047185943074

temporal_extent_start="2023-08-04T00:00:00.000Z"
temporal_extent_end="2023-09-01T00:00:00.000Z"


request = {
    "input": {
        "bounds": {
            "bbox": [
                west,
                south,
                east,
                north
            ],
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
        },
        "data": [
            {
                "type": "sentinel-1-grd",
                "dataFilter": {
                    "timeRange": {
                        "from": temporal_extent_start,
                        "to": temporal_extent_end,
                    },
                    "acquisitionMode": "IW",
                    "polarization": "DV",
                    "orbitDirection ": "ASCENDING",
                },
                "processing": {
                    "backCoeff": "GAMMA0_ELLIPSOID",
                    "orthorectify": "true",
                },
            }
        ],
    },
    "output": {
        "width": 1000,
        "height": 1000,
        "responses": [
            {
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }
        ],
    },
    "evalscript": evalscript,
}

url = "https://sh.dataspace.copernicus.eu/api/v1/process"
response = oauth.post(url, json=request, headers={"Accept": "image/tiff"})

url = "https://sh.dataspace.copernicus.eu/api/v1/process"
response = oauth.post(url, json=request, headers={"Accept": "image/tiff"})
# All requests using this session will have an access token automatically added
print(response.content)

if response.status_code == 200:
    local_file_path= "test.tif"
    with open(local_file_path, "wb") as file:
        file.write(response.content)
        print("Wrote to file: {}".format(local_file_path))
else:
    print("Request failed with code: {}".format(response.status_code))
    print("Message: {}".format(response.text))

# url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/collections/"
# response_collections = oauth.get(url)
# print(response_collections.content)
# if response_collections.status_code == 200:
#     print("Request succeeded")
#     json_data=response_collections.content
#     data_dict=json.loads(json_data)
#     df=pd.DataFrame.from_dict(data_dict['collections'])
#     print(df)
# else:
#     print("Request failed with code: {}".format(response_collections.status_code))
#     print("Message: {}".format(response_collections.text))