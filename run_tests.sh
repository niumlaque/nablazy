#!/bin/bash

set -e

echo "Starting integration tests..."

# アプリケーションが起動していない場合は起動
if ! docker compose ps | grep -q "ytdl-app.*Up"; then
    echo "Starting application..."
    docker compose up -d
    echo "Waiting for application to be ready..."
    sleep 15
else
    echo "Application is already running"
fi

# コンテナ内で統合テストを実行
echo "Running integration tests inside container..."
docker compose exec nablazy-app python3 -m unittest test_integration -v

echo "Integration tests completed!"

