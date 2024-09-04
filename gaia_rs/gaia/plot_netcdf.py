import rasterio
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import rasterio
from rasterio import transform

from gaia_rs.gaia.aux import histogram_3band_equalization

# Read the NetCDF file
path=r'/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/ncdf'
file=path+r'/openEO_cCDCWQn.nc'
ds = xr.open_dataset(file)

# Extract the individual bands
red_band = ds['B02']
green_band = ds['B03']
blue_band = ds['B04']

# Convert the bands to NumPy arrays
red = red_band.values
green= green_band.values
blue = blue_band.values
normalized_red = (red - np.nanmin(red)) / (np.nanmax(red) - np.nanmin(red))
normalized_green = (green - np.nanmin(green)) / (np.nanmax(green) - np.nanmin(green))
normalized_blue = (blue - np.nanmin(blue)) / (np.nanmax(blue) - np.nanmin(blue))

# Combine colors into RGB array
# Create a new NetCDF file with the RGB bands combined
rgb_array = np.stack([normalized_red, normalized_green, normalized_blue], axis=0)
rgb_dataset = xr.DataArray(rgb_array[0], coords=ds.coords, dims=['t', 'y', 'x'])
rgb_dataset = rgb_dataset.astype(int)
rgb_dataset = rgb_dataset.transpose('y', 'x', 't')

# Create a new figure and axes
fig, ax = plt.subplots(1, 1)

extent = [ds.coords['x'].isel(x=0).item(), ds.coords['x'].isel(x=-1).item(),
          ds.coords['y'].isel(y=0).item(), ds.coords['y'].isel(y=-1).item()]
# Plot the RGB data
im = ax.imshow(rgb_dataset, extent=extent, aspect='auto')

# Add colorbar
fig.colorbar(im, label='RGB')

# Set title
ax.set_title('RGB Data')

# Show the plot
plt.show()

output_geotiff = f'test.tif'
crs='+proj=latlong'
with rasterio.open(output_geotiff, 'w', driver='GTiff', height=red_band.sizes['y'], width=red_band.sizes['x'],
                           count=3, dtype=str(rgb_array.dtype), crs=crs, transform=transform) as dst:
            dst.write(rgb_array, [1,2,3])



histogram_3band_equalization(output_geotiff)

print('done')


