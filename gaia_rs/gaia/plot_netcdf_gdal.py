import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin
from gaia_rs.gaia.aux import histogram_3band_equalization
from matplotlib import pyplot as plt
from skimage import exposure

# Read the NetCDF file
file = '/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/ncdf/openEO_cCDCWQn.nc'
ds = xr.open_dataset(file)

# Get the x and y coordinate information
x_coords, y_coords = ds.coords['x'], ds.coords['y']

# Calculate the north, south, east, and west extent
north, south = y_coords.max(), y_coords.min()
east, west = x_coords.max(), x_coords.min()

# Calculate the longitude and latitude resolution
lon_resolution, lat_resolution = (east - west) / ds.dims['x'], (north - south) / ds.dims['y']

# Define the transform
transform = from_origin(west, north, lon_resolution, lat_resolution)

# Loop over the time dimension
for t in range(ds.dims['t']):
    date = str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
    output_geotiff = f'_{date}.tif'

    # Extract and normalize the bands
    rgb_array = np.stack([(ds.isel(t=t)[band] - ds.isel(t=t)[band].min()) /
                          (ds.isel(t=t)[band].max() - ds.isel(t=t)[band].min())
                          for band in ['B03', 'B04', 'B02']], axis=0)
    #remove nan values
    rgb_array = np.nan_to_num(rgb_array)
    # Enhance the histogram using histogram equalization
    rgb_array = exposure.equalize_hist(rgb_array.astype("float"))

    # Convert the enhanced array back to uint8 format
    rgb_array = np.uint8(rgb_array * 255)
    rgb_array = np.transpose(rgb_array, (1, 2, 0))
    plt.figure(figsize=(10, 10))
    plt.imshow(rgb_array, extent=[west, east, south, north])
    plt.colorbar()
    plt.title("RGB Image from NetCDF Bands")
    plt.show()
#plot histogram of rgb array
    plt.figure(figsize=(10, 10))
    plt.hist(rgb_array.ravel(), bins=256, range=(0.0, 1.0), fc='k', ec='k')
    plt.title("Histogram of RGB Image")
    plt.show()
    
    # Write the RGB array to a GeoTIFF file
    with rasterio.open(output_geotiff, 'w', driver='GTiff', height=ds.dims['y'], width=ds.dims['x'],
                       count=3, dtype=str(rgb_array.dtype), crs='+proj=latlong', transform=transform) as dst:
        dst.write(rgb_array, [1,2,3])

    # Apply histogram equalization
    #histogram_3band_equalization(output_geotiff)

print('done')