#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
# Automatic export to the environment of subsequently executed commands
# source: the command 'help export' run in Terminalexport IMAGE_NAME="rag-detective-frontend-simple"export IMAGE_NAME="rag-detective-frontend-simple"
export IMAGE_NAME="rag-detective-frontend-simple"
export BASE_DIR=$(pwd)

# Ask the user which environment to use
echo "Select the Docker environment:"
echo "1) Development"
echo "2) Production"
read -p "Enter your choice (1 or 2): " ENV_CHOICE

# Set the Dockerfile and container port based on the user's choice
case $ENV_CHOICE in
    1)
        DOCKERFILE="Dockerfile.dev"
        CONTAINER_PORT=8080
        ;;
    2)
        DOCKERFILE="Dockerfile"
        CONTAINER_PORT=80
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Echo commands for debugging
echo "Building image with: docker build -t $IMAGE_NAME -f $DOCKERFILE ."
echo "Running container on port: $CONTAINER_PORT"

# Build the image based on the chosen Dockerfile
docker build -t $IMAGE_NAME -f $DOCKERFILE .

# Run the container
# --v: Attach a filesystem volume to the container
# -p: Publish a container's port(s) to the host (host_port: container_port) (source: https://dockerlabs.collabnix.com/intermediate/networking/ExposingContainerPort.html)
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-p 8080:$CONTAINER_PORT $IMAGE_NAME
