# Create your tasks here
import json
import os
import geopandas
import shapely
from celery import shared_task
import openeo
from celery.signals import task_success, task_prerun, task_postrun


@shared_task
def add(x, y):
    return x + y

@task_success.connect(sender=add)
def task_success_notifier(sender=None, **kwargs):
    print("From task_success_notifier ==> Task run successfully!")

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


