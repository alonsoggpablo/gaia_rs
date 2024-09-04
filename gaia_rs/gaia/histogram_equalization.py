import os
import time

import numpy as np
import cv2
from matplotlib import pyplot as plt
import rasterio


def showimage(myimage, figsize=[10, 10]):
    if (myimage.ndim > 2):  # This only applies to RGB or RGBA images (e.g. not to Black and White images)
        myimage = myimage[:, :, ::-1]  # OpenCV follows BGR order, while matplotlib likely follows RGB order

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(myimage, cmap='gray', interpolation='bicubic')
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

def histogram_3bands_equalization_test(raster_file):

    # Open the GeoTIFF file.
    #with rasterio.open('/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/raster_files/valladolid_rgb_2023_07_10.tif') as src:
    with rasterio.open(raster_file,'r',driver='GTiff') as src:
        img = src.read()

    img=img*255
    # Check the minimum and maximum values in the array
    min_value = np.min(img)
    max_value = np.max(img)

    # Normalize the values in the array if they are outside of the range 0-255
    if min_value < 0 or max_value > 255:
        img = (img - min_value) / (max_value - min_value) * 255
    # Suppress/hide the warning
    np.seterr(invalid='ignore')
    # Cast the array to `np.uint8` and replace invalid values with 0
    img = np.clip(img, 0, 255).astype(np.uint8)


    #img = (img * 255).astype(np.uint8)


    # Remove NaN values from the image.
    img[:, :, 0] = np.nan_to_num(img[:, :, 0])
    img[:,:, 1] = np.nan_to_num(img[:, :, 1])
    img[:,:, 2] = np.nan_to_num(img[:, :, 2])

    # Using Numpy to calculate the histogram
    color = ('b','g','r')
    for i,col in enumerate(color):
        histr, _ = np.histogram(img[:,:,i],256,[0,256])
        plt.plot(histr,color = col)
        plt.xlim([0,256])
    plt.show()

    # For ease of understanding, we explicitly equalize each channel individually
    colorimage_r = cv2.equalizeHist(img[0,:, :].astype(np.uint8))
    colorimage_g = cv2.equalizeHist(img[1,:, :].astype(np.uint8))
    colorimage_b = cv2.equalizeHist(img[2,:, :].astype(np.uint8))

    # Next we stack our equalized channels back into a single image
    colorimage_e = np.stack((colorimage_b, colorimage_g, colorimage_r), axis=2)
    colorimage_e.shape


    # Using Numpy to calculate the histogram
    color = ('b','g','r')
    for i,col in enumerate(color):
        histr, _ = np.histogram(colorimage_e[i,:,:],256,[0,256])
        plt.plot(histr,color = col)
        plt.xlim([0,256])
    plt.show()

    img=img.transpose(1,2,0)

    # Using Numpy's function to append the two images horizontally
    side_by_side = np.hstack((img,colorimage_e))
    showimage(side_by_side,[20,10])

    colorimage_e=colorimage_e.transpose(2,0,1)

    # Save the processed image to a new GeoTIFF file.
    with rasterio.open(raster_file, "w", **src.meta) as dst:
        dst.write(colorimage_e)



    # Close the GeoTIFF files.
    src.close()
    time.sleep(30)
    dst.close()
#histogram_3bands_equalization_test('/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/raster_files/barrios_de_luna_rgb_2023_07_25_bKUdo3m.tif')



def plot_rgb_pseudocolor_image(raster_path):
  """Plots an RGB pseudocolor image from a single band raster.

  Args:
    raster_path: The path to the single band raster.
  """

  # Read the raster data.
  with rasterio.open(raster_path) as src:
    raster_data = src.read()

    new_image = np.zeros((raster_data.shape[1], raster_data.shape[2]), dtype=np.uint8)

    # Assign the normalized raster values to the RGB channels of the new image.
    new_image[:, :] = raster_data*255
    #new_image[:, :, 1] = normalized_raster_data* 255
    #new_image[:, :, 2] = normalized_raster_data*100

    # Plot the new image.
    plt.imshow(new_image)
    plt.show()

    # Save the processed image to a new GeoTIFF file.
    #with rasterio.open(raster_path, "w", **src.meta) as dst:
    #   dst.write(new_image)
    with rasterio.open(raster_path, "w", **src.meta) as dst:
        dst.write(new_image, 1)
  # Close the GeoTIFF files.
  src.close()
  dst.close()

# Create a pseudocolor image.
#plot_rgb_pseudocolor_image("/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/raster_files/barrios_de_luna_moisture_2023_07_20.tif")


def plot_histogram(img):
    #img = cv2.imread(file)
    img = cv2.equalizeHist(img)
    assert img is not None, "file could not be read, check with os.path.exists()"
    color = ('b','g','r')
    for i,col in enumerate(color):
        histr = cv2.calcHist([img],[i],None,[256],[0,256])
        plt.plot(histr,color = col)
        plt.xlim([0,256])
    plt.show()

file=r'/Users/pabloalonso/Documents/GitHub/gaia_rs/gaia_rs/media/raster_files/barrios_de_luna_rgb_2023_07_25_bKUdo3m.tif'
with rasterio.open(file) as src:
    rgb_img=src.read()
plot_histogram(rgb_img)