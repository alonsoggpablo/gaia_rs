import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# Load the NetCDF file
netcdf_file = 'openEO.nc'  # Replace with your NetCDF file path
ds = xr.open_dataset(netcdf_file)

# Select bands (NIR and Red) for NDVI calculation
nir = ds['B08']
red = ds['B04']

# Calculate NDVI
ndvi = (nir - red) / (nir + red)

# Plot NDVI intensity map
for t in range(0,ds.dims['t']):
    date=str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
    plt.figure(figsize=(10, 8))
    plt.imshow(ndvi.isel(t=t), cmap='RdYlGn', vmin=-1, vmax=1)  # Adjust colormap and limits
    plt.colorbar(label='NDVI')
    plt.title(f'NDVI Intensity Map  - {date}')
    plt.savefig(f'ndvi_{date}.png')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
