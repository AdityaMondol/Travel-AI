#!/bin/bash

echo "Building TravelAI Docker image..."
docker build -t travelai:latest .

echo "Starting TravelAI container..."
docker-compose up -d

echo "Waiting for service to be ready..."
sleep 10

echo "Checking health..."
curl http://localhost:8000/health

echo "TravelAI is running at http://localhost:8000"
