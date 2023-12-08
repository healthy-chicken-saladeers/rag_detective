"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py --train
"""

import os
import argparse
from glob import glob
import random
import string
import google.cloud.aiplatform as aip

GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_PACKAGE_URI = os.environ["GCS_PACKAGE_URI"]
GCP_REGION = os.environ["GCP_REGION"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]


def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def main(args=None):
    if args.train:
        print("Train Model")

        # Initialize Vertex AI SDK for Python
        aip.init(
            project=GCP_PROJECT, location=GCP_REGION, staging_bucket=GCS_PACKAGE_URI
        )

        job_id = generate_uuid()
        DISPLAY_NAME = "ragdetective_" + job_id

        # container_uri = "us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12.py310:latest"
        container_uri = "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest"
        python_package_gcs_uri = f"{GCS_PACKAGE_URI}/trainer.tar.gz"

        job = aip.CustomPythonPackageTrainingJob(
            display_name=DISPLAY_NAME,
            python_package_gcs_uri=python_package_gcs_uri,
            python_module_name="trainer.task",
            container_uri=container_uri,
            project=GCP_PROJECT,
        )

        CMDARGS = ["--epochs=2", "--batch_size=8", f"--bucket_name={GCS_BUCKET_NAME}"]
        MODEL_DIR = GCS_PACKAGE_URI
        TRAIN_COMPUTE = "n1-standard-4"
        TRAIN_GPU = "NVIDIA_TESLA_T4"
        TRAIN_NGPU = 1

        print(python_package_gcs_uri)

        # Run the training job on Vertex AI
        # sync=True, # If you want to wait for the job to finish
        job.run(
            model_display_name=None,
            args=CMDARGS,
            replica_count=1,
            machine_type=TRAIN_COMPUTE,
            # accelerator_type=TRAIN_GPU,
            # accelerator_count=TRAIN_NGPU,
            base_output_dir=MODEL_DIR,
            sync=False,
        )


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Collector CLI")

    parser.add_argument(
        "-t",
        "--train",
        action="store_true",
        help="Train model",
    )

    args = parser.parse_args()

    main(args)
