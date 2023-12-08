#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="financial-sentiment-model"
export BASE_DIR=$(pwd)
export MODEL_DIR=$(pwd)/best_model 

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$MODEL_DIR":/model \
-p 8000:8080 \
$IMAGE_NAME
