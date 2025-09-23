#!/bin/bash

# Docker Hub deployment script for Cineulagam Publisher
# Make sure you're logged in to Docker Hub: docker login

# Configuration
DOCKER_USERNAME="your-dockerhub-username"  # Replace with your Docker Hub username
IMAGE_NAME="cineulagam-publisher"
TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "Building Docker image: ${FULL_IMAGE_NAME}"

# Build the image
docker build -t ${FULL_IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo "Build successful! Pushing to Docker Hub..."
    
    # Push to Docker Hub
    docker push ${FULL_IMAGE_NAME}
    
    if [ $? -eq 0 ]; then
        echo "Successfully pushed ${FULL_IMAGE_NAME} to Docker Hub!"
        echo "You can now pull and run with:"
        echo "docker run -p 5000:5000 ${FULL_IMAGE_NAME}"
    else
        echo "Failed to push to Docker Hub. Make sure you're logged in with 'docker login'"
        exit 1
    fi
else
    echo "Build failed!"
    exit 1
fi
