import xarray as xr
import matplotlib.pyplot as plt

ds = xr.load_dataset("OpenEO.nc")

# Create the RGB image using B02, B03, B04 bands
# Extract the NO2 variable (assuming 'no2' is the variable name)
no2 = ds['NO2'].fillna(0)


# Plot the NO2 intensity map
for t in range(0,ds.dims['t']):

    plt.imshow(no2.isel(t=t), cmap='RdYlGn')  # Adjust colormap and limits
    plt.colorbar(label='NO2 Intensity')
    plt.title('NO2 Intensity Map')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

# Close the dataset after use
ds.close()

