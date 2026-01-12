#!/bin/bash

# Docker Quick Start Script for ClaimSphere AI

set -e

echo "🚀 Starting ClaimSphere AI with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running."
    echo ""
    echo "📋 Please start Docker Desktop:"
    echo "   1. Open Docker Desktop from Applications"
    echo "   2. Wait for Docker to start (whale icon in menu bar)"
    echo "   3. Run this script again: ./docker-start.sh"
    echo ""
    echo "💡 Or try: open -a Docker"
    exit 1
fi

echo "✅ Docker is running!"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.template .env
    echo "📝 Please edit .env and add your API keys:"
    echo "   - QIANFAN_API_KEY (required for CAMEL-AI)"
    echo "   - BAIDU_API_KEY and BAIDU_SECRET_KEY (optional, for fallback)"
    echo ""
    read -p "Press Enter after adding your API keys..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Use docker compose (v2) if available, otherwise fall back to docker-compose (v1)
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    echo "✅ Using Docker Compose v2"
else
    COMPOSE_CMD="docker-compose"
    echo "✅ Using Docker Compose v1"
fi

# Build and start services
echo "🔨 Building Docker images..."
$COMPOSE_CMD build

echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if $COMPOSE_CMD exec -T db pg_isready -U claimsphere > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for database... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  Database may not be ready. Continuing anyway..."
fi

# Run migrations
echo "📊 Running database migrations..."
$COMPOSE_CMD exec -T backend alembic upgrade head 2>&1 || echo "⚠️  Migrations may have failed. Check logs with: $COMPOSE_CMD logs backend"

echo ""
echo "✅ ClaimSphere AI is starting!"
echo ""
echo "📍 Services:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: $COMPOSE_CMD logs -f backend"
echo "   - Stop services: $COMPOSE_CMD down"
echo "   - Restart: $COMPOSE_CMD restart backend"
echo ""
echo "📖 See DOCKER_SETUP.md for more information"
