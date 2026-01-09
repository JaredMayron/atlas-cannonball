#!/bin/bash
set -e

# Required variables
PROJECT_ID=$1
REGION=$2
REPO_NAME=$3
IMAGE_NAME=$4

if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ] || [ -z "$REPO_NAME" ] || [ -z "$IMAGE_NAME" ]; then
    echo "Usage: ./bootstrap_image.sh <PROJECT_ID> <REGION> <REPO_NAME> <IMAGE_NAME>"
    exit 1
fi

FULL_IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"

echo "Checking if image exists: $FULL_IMAGE_NAME"

# Check if the image exists in Artifact Registry
if gcloud artifacts docker images describe "$FULL_IMAGE_NAME" > /dev/null 2>&1; then
    echo "Image exists. Skipping bootstrap build."
else
    echo "Image not found. Building and pushing initial image..."
    
    # Authenticate Docker to Artifact Registry
    gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

    # Navigate to the correct directory (assuming script is in GCP/scripts)
    cd "$(dirname "$0")/.."

    # Build the image
    docker build -t "$FULL_IMAGE_NAME" .

    # Push the image
    docker push "$FULL_IMAGE_NAME"
    
    echo "Bootstrap build complete."
fi
