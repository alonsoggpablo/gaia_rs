import openeo

# First, we connect to the back-end and authenticate.
connection = openeo.connect("openeo.dataspace.copernicus.eu")
connection.authenticate_oidc()

# Now that we are connected, we can initialize our datacube object with the area of interest
# and the time range of interest using Sentinel 1 data.
sentinel2_cube = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent={"west": 5.14, "south": 51.17, "east": 5.17, "north": 51.19},
    temporal_extent = ["2021-02-01", "2021-04-30"],
    bands=["B02", "B04", "B08","SCL"],
    max_cloud_cover=85,
)

# By filtering as early as possible (directly in load_collection() in this case),
# we make sure the back-end only loads the data we are interested in and avoid incurring unneeded costs.


#From this data cube, we can now select the individual bands with the DataCube.band() method and rescale the digital number values to physical reflectances:
blue = sentinel2_cube.band("B02") * 0.0001
red = sentinel2_cube.band("B04") * 0.0001
nir = sentinel2_cube.band("B08") * 0.0001


# We now want to compute the enhanced vegetation index and can do that directly with these band variables:
evi_cube = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1.0)

# Now we can use the compact “band math” feature again to build a binary mask with a simple comparison operation:
# Select the "SCL" band from the data cube
scl_band = sentinel2_cube.band("SCL")
# Build mask to mask out everything but class 4 (vegetation)
mask = (scl_band != 4)

# Before we can apply this mask to the EVI cube we have to resample it, as the “SCL” layer has a “ground sample distance” of 20 meter, while it is 10 meter for the “B02”, “B04” and “B08” bands. We can easily do the resampling by referring directly to the EVI cube.
mask_resampled = mask.resample_cube_spatial(evi_cube)

# Apply the mask to the `evi_cube`
evi_cube_masked = evi_cube.mask(mask_resampled)

# Because GeoTIFF does not support a temporal dimension, we first eliminate it by taking the temporal maximum value for each pixel:
evi_composite = evi_cube.max_time()

# Now we can download this to a local file:
evi_composite.download("evi-composite.tiff")
