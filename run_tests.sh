#!/bin/bash

set -e

echo "Starting integration tests..."

# Start application if not running
if ! docker compose ps | grep -q "nablazy-app.*Up"; then
    echo "Starting application..."
    docker compose up -d
    echo "Waiting for application to be ready..."
    sleep 15
else
    echo "Application is already running"
fi

# Run integration tests inside container
echo "Running integration tests inside container..."
docker compose exec nablazy-app python3 -m unittest test_integration -v

echo "Integration tests completed!"

