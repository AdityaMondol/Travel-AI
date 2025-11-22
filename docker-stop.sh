#!/bin/bash

echo "Stopping TravelAI container..."
docker-compose down

echo "Removing TravelAI image..."
docker rmi travelai:latest

echo "Cleanup complete"
