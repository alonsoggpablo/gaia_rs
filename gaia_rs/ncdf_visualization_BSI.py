import xarray as xr
import matplotlib.pyplot as plt

ds = xr.load_dataset("OpenEO.nc")

# Create the RGB image using B02, B03, B04 bands
b08 = ds['B08']
b04 = ds['B04']
b02= ds['B02']
b11= ds['B11']

bsi=((b11+b04)-(b08+b02))/((b11+b04)+(b08+b02))


# Plot NDVI intensity map
for t in range(0,ds.dims['t']):
    date=str(ds.isel(t=t).t.dt.day.astype(str))[-10:]
    plt.figure(figsize=(10, 8))
    plt.imshow(bsi.isel(t=t), cmap='RdYlGn', vmin=-1, vmax=1)  # Adjust colormap and limits
    plt.colorbar(label='NDVI')
    plt.title(f'BSI Intensity Map  - {date}')
    plt.savefig(f'bsi_{date}.png')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()



