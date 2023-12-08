#!/bin/bash

rm -f trainer.tar trainer.tar.gz
tar cvf trainer.tar package
gzip trainer.tar

set -e
export IMAGE_NAME=model-training-cli
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/secrets/
export GCS_BUCKET_URI="gs://sentiment-trainer"
export GCP_PROJECT="rag-detective"
export WANDB_KEY=$WANDB_KEY

echo WANDB_KEY
echo $WANDB_KEY
# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
#docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=secrets/model_trainer.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_URI=$GCS_BUCKET_URI \
-e WANDB_KEY=$WANDB_KEY \
$IMAGE_NAME