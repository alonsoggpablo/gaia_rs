import xarray as xr
import matplotlib.pyplot as plt

ds = xr.load_dataset("OpenEO.nc")

# Create the RGB image using B02, B03, B04 bands
data = ds[["B04", "B08","B02","B11]].to_array(dim="bands")

# Para arrays de varios instantes de tiempo
for t in range(0,ds.dims['t']):
    data[{"t": t}].plot.imshow(vmin=0, vmax=2000)
    plt.show()

#Para arrays de varios instantes de tiempo, pero solo el último
#data[{"t": -1}].plot.imshow(vmin=0, vmax=2000)
#plt.show()

# Para arrays de 1 instante de tiempo
#data.plot.imshow(vmin=0, vmax=2000)
#plt.show()


