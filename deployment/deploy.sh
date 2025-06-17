#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ubuntu/Ego_AI"
cd "$APP_DIR"

echo "Pulling latest code..."
git reset --hard
git pull origin main

echo "Rebuilding and restarting containers..."
docker-compose down
docker-compose pull
docker-compose build
docker-compose up -d

echo "Deployed successfully!"
