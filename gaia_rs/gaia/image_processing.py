import numpy as np
import matplotlib.pyplot as plt
import rasterio
from skimage import img_as_ubyte
from skimage.exposure import equalize_hist

file = r'/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/raster_files/barrios_de_luna_rgb_2023_08_09.tif'

def equalized_histogram(file):
    with rasterio.open(file) as src:
        red_band = src.read(1)
        green_band = src.read(2)
        blue_band = src.read(3)

    # Stack the bands together
    rgb_array = np.dstack((red_band, green_band, blue_band))

    # Convert the image to byte format
    rgb_array = img_as_ubyte(rgb_array)

    # Equalize the histogram
    rgb_equalized = equalize_hist(rgb_array)

    return rgb_array,rgb_equalized

rgb_equalized = equalized_histogram(file)[1]
rgb_array = equalized_histogram(file)[0]
#plot the image

plt.imshow(rgb_array)
plt.show()
plt.imshow(rgb_equalized)
plt.show()


def plot_histogram(rgb_image):

    # Separate the channels
    red_channel = rgb_image[:, :, 0]
    green_channel = rgb_image[:, :, 1]
    blue_channel = rgb_image[:, :, 2]

    # Create a new figure
    plt.figure(figsize=(10, 4))

    # Plot the histogram of the red channel
    plt.subplot(1, 3, 1)
    plt.hist(red_channel.flatten(), bins=256, color='red', alpha=0.7)
    plt.title('Red Channel Histogram')

    # Plot the histogram of the green channel
    plt.subplot(1, 3, 2)
    plt.hist(green_channel.flatten(), bins=256, color='green', alpha=0.7)
    plt.title('Green Channel Histogram')

    # Plot the histogram of the blue channel
    plt.subplot(1, 3, 3)
    plt.hist(blue_channel.flatten(), bins=256, color='blue', alpha=0.7)
    plt.title('Blue Channel Histogram')

    # Display the histograms
    plt.tight_layout()
    plt.show()

plot_histogram(rgb_array)
plot_histogram(rgb_equalized)