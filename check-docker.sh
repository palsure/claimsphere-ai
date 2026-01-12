#!/bin/bash

# Check Docker status script

echo "🔍 Checking Docker status..."

# Check if Docker command exists
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if docker info > /dev/null 2>&1; then
    echo "✅ Docker is running!"
    echo ""
    echo "🐳 Docker version:"
    docker --version
    echo ""
    echo "📦 Docker Compose version:"
    docker-compose --version 2>/dev/null || docker compose version
    echo ""
    echo "🚀 You can now run: ./docker-start.sh"
else
    echo "❌ Docker daemon is not running."
    echo ""
    echo "📋 To start Docker:"
    echo "   1. Open Docker Desktop application"
    echo "   2. Wait for Docker to start (whale icon in menu bar)"
    echo "   3. Run this script again: ./check-docker.sh"
    echo ""
    echo "💡 Or try: open -a Docker"
    exit 1
fi
