# Create your tasks here
import json
import os
import time

import cv2
import geopandas
import numpy as np
import rasterio
import shapely
from celery import shared_task
import openeo
from celery.signals import task_success, task_prerun, task_postrun


@shared_task
def run_batch_job_process_datacube(cube_dict,datacube_id):
    # Initialize the OpenEO connection with your credentials
    connection = openeo.connect('openeo.dataspace.copernicus.eu')
    connection.authenticate_oidc()

    cube = connection.load_collection(
        cube_dict['collection'],
        bands=cube_dict['bands'],
        temporal_extent=cube_dict['temporal_extent'],
        spatial_extent=cube_dict['spatial_extent'],
        max_cloud_cover=cube_dict['max_cloud_cover'],
    )

    if cube_dict['category'] == 'SAR':
        cube = cube.sar_backscatter(coefficient="sigma0-ellipsoid")

    job = cube.execute_batch(output_format='netcdf', format='netcdf')
    job_id = job.job_id
    download_copernicus_results.delay(job_id, datacube_id)


@shared_task
def download_copernicus_results(job_id,datacube_id):
    # Initialize the OpenEO connection with your credentials
    connection = openeo.connect('openeo.dataspace.copernicus.eu')
    connection.authenticate_oidc()

    try:
        # Get the batch job status
        job = connection.job(job_id)
        results = job.get_results()
        # Check if the job is finished
        if job.status() == 'finished':
            # Download the results
            results.download_files('')
            print ('NetCDF download finished')
            return f"{datacube_id}"
        else:
            return f"Job status is not 'finished': {job.status()}"
    except Exception as e:
        return f"Error while downloading results: {str(e)}"


def sync_batch_job_process_datacube(cube_dict,datacube_id):
    # Initialize the OpenEO connection with your credentials
    connection = openeo.connect('openeo.dataspace.copernicus.eu')
    connection.authenticate_oidc()

    cube = connection.load_collection(
        cube_dict['collection'],
        #bands=cube_dict['bands'],
        temporal_extent=cube_dict['temporal_extent'],
        spatial_extent=cube_dict['spatial_extent'],
        max_cloud_cover=cube_dict['max_cloud_cover'],
    )

    if cube_dict['category'] == 'SAR':
        cube = cube.sar_backscatter(coefficient="sigma0-ellipsoid")

    job = cube.execute_batch(format='GTiff')
    job_id = job.job_id
    results = job.get_results()
    for asset in results.get_assets():
        if asset.metadata["type"].startswith("image/tif"):
            asset.download(asset.name)





