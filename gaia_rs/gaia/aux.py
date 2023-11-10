import cv2
import numpy as np
import rasterio


def histogram_3band_equalization(raster_file):
    # Open the GeoTIFF file.
    with rasterio.open(raster_file,'r',driver='GTiff') as src:
        img = src.read()
    img = img * 255
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

    # Remove NaN values from the image.
    img[:, :, 0] = np.nan_to_num(img[:, :, 0])
    img[:,:, 1] = np.nan_to_num(img[:, :, 1])
    img[:,:, 2] = np.nan_to_num(img[:, :, 2])

    # For ease of understanding, we explicitly equalize each channel individually
    colorimage_r = cv2.equalizeHist(img[0,:, :].astype(np.uint8))
    colorimage_g = cv2.equalizeHist(img[1,:, :].astype(np.uint8))
    colorimage_b = cv2.equalizeHist(img[2,:, :].astype(np.uint8))

    # Next we stack our equalized channels back into a single image
    colorimage_e = np.stack((colorimage_b, colorimage_g, colorimage_r), axis=2)

    colorimage_e=colorimage_e.transpose(2,0,1)

    # Save the processed image to a new GeoTIFF file.
    with rasterio.open(raster_file, "w", **src.meta) as dst:
        dst.write(colorimage_e)

    # Close the GeoTIFF files.
    src.close()
    dst.close()


def single_band_pseudocolor_image(raster_file):
  with rasterio.open(raster_file) as src:
    raster_data = src.read()

    new_image = np.zeros((raster_data.shape[1], raster_data.shape[2]), dtype=np.uint8)

    # Assign the normalized raster values to the RGB channels of the new image.
    new_image[:, :] = raster_data*255

    with rasterio.open(raster_file, "w", **src.meta) as dst:
        dst.write(new_image, 1)
  # Close the GeoTIFF files.
  src.close()
  dst.close()
