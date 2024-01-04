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



def sync_sentinel_hub_s2(north,south,east,west,temporal_extent_start,temporal_extent_end):
    evalscript = """
        //VERSION=3

        function setup() {
  return{
    input: [{bands:["B02", "B03", "B04", "AOT", "SCL", "SNW", "CLD", "sunAzimuthAngles", "sunZenithAngles", "viewAzimuthMean", "viewZenithMean"]}],
    output: [
        {id: "TrueColor", bands: 3, sampleType: SampleType.FLOAT32},
        {id: "AOT", bands: 1, sampleType: SampleType.UINT16},
        {id: "SCL", bands: 1, sampleType: SampleType.UINT8},
        {id: "SNW", bands: 1, sampleType: SampleType.UINT8},
        {id: "CLD", bands: 1, sampleType: SampleType.UINT8},
        {id: "SAA", bands: 1, sampleType: SampleType.FLOAT32},
        {id: "SZA", bands: 1, sampleType: SampleType.FLOAT32},
        {id: "VAM", bands: 1, sampleType: SampleType.FLOAT32},
        {id: "VZM", bands: 1, sampleType: SampleType.FLOAT32}
    ]
  }
}

function evaluatePixel(sample) {
    var truecolor = [sample.B04, sample.B03, sample.B02]
    var aot = [sample.AOT]
    var scl = [sample.SCL]
    var snw = [sample.SNW]
    var cld = [sample.CLD]
    var saa = [sample.sunAzimuthAngles]
    var sza = [sample.sunZenithAngles]
    var vam = [sample.viewAzimuthMean]
    var vzm = [sample.viewZenithMean]

    return {
        TrueColor: truecolor,
        AOT: aot,
        SCL: scl,
        SNW: snw,
        CLD: cld,
        SAA: saa,
        SZA: sza,
        VAM: vam,
        VZM: vzm
    }

}
    """

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
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": temporal_extent_start,
                        "to": temporal_extent_end,
                    }
                },
            }
        ],
    },
    "output": {
        "width": 1000,
        "height": 1000,
        "responses": [
            {
                "identifier": "TrueColor",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "AOT",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "SCL",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "SNW",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "CLD",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "SAA",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "SZA",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "VAM",
                "format": {
                    "type": "image/tiff"
                }
            },
            {
                "identifier": "VZM",
                "format": {
                    "type": "image/tiff"
                }
            }
        ],
    },
    "evalscript": evalscript,
}

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=request, headers={"Accept": "application/tar"})
    # All requests using this session will have an access token automatically added
    print(response.content)

    if response.status_code == 200:
        local_file_path= "sentinel2.tar"
        with open(local_file_path, "wb") as file:
            file.write(response.content)
            print("Wrote to file: {}".format(local_file_path))
    else:
        print("Request failed with code: {}".format(response.status_code))
        print("Message: {}".format(response.text))

# north=41.415843680127004
# south=41.20886048278024
# east=-4.515979965182463
# west=-5.005047185943074
#
# temporal_extent_start="2023-08-04T00:00:00.000Z"
# temporal_extent_end="2023-09-01T00:00:00.000Z"
# sync_sentinel_hub_s2(north,south,east,west,temporal_extent_start,temporal_extent_end)