#!/bin/bash

# Make executable using chmod +x deploy.sh

echo "Pulling the latest changes from the git repository..."
git pull

echo "Taking down the existing Docker containers..."
docker-compose -f docker-compose-deploy.yml down

echo "Building the app..."
docker-compose -f docker-compose-deploy.yml build app

echo "Bringing up the Docker containers in detached mode..."
docker-compose -f docker-compose-deploy.yml up -d

echo "Done."