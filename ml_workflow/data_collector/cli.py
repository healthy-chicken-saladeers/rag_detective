import os
import argparse
from glob import glob
import zipfile
import os
import requests
import zipfile
import tarfile
import time
import argparse
from google.cloud import storage

dataset_folder = os.path.join("data")

def main(args=None):

    GCS_BUCKET_NAME = "rag-detective-ml-workflow"

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(GCS_BUCKET_NAME)

    zip_file = os.path.join(dataset_folder, "v1.0.zip")
    blob = bucket.blob("v1.0.zip")
    blob.upload_from_filename(zip_file)

if __name__ == "__main__":

    main()




