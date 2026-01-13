# Docker Setup Guide for ClaimSphere AI

This guide explains how to run ClaimSphere AI locally using Docker and Docker Compose.

## Prerequisites

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **API Keys** (see below)

### Install Docker

**macOS:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or using Homebrew:
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

Verify installation:
```bash
docker --version
docker-compose --version
```

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp env.template .env
```

Edit `.env` and add your API keys:

```env
# Required for CAMEL-AI multi-agent system
QIANFAN_API_KEY=ak-your-qianfan-api-key-here

# Optional: For fallback mode
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key

# JWT Secret (change in production!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

**Get your API keys:**
- **Qianfan API Key**: https://console.bce.baidu.com/qianfan/overview
- **Baidu AI Studio**: https://aistudio.baidu.com

See `docs/CAMEL_AI_SETUP.md` for detailed API key setup.

### 2. Build and Start Services

**Start all services (database + backend):**
```bash
docker-compose up -d
```

**Start with development overrides (hot-reload enabled):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**View logs:**
```bash
docker-compose logs -f backend
```

### 3. Initialize Database

Run database migrations:

```bash
# Enter the backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

Or run migrations from outside:
```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Docker Commands

### Start Services
```bash
# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up db
docker-compose up backend
```

### Stop Services
```bash
# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (⚠️ deletes database data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Execute Commands in Container
```bash
# Enter backend container
docker-compose exec backend bash

# Run Python commands
docker-compose exec backend python -c "import camel; print(camel.__version__)"

# Run migrations
docker-compose exec backend alembic upgrade head

# Run tests
docker-compose exec backend pytest tests/
```

### Rebuild After Code Changes
```bash
# Rebuild backend image
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

## Configuration

### Environment Variables

Environment variables can be set in:
1. `.env` file (recommended)
2. `docker-compose.yml` (default values)
3. Command line: `docker-compose up -e QIANFAN_API_KEY=xxx`

### Database Configuration

Default database settings:
- **Host**: `db` (service name)
- **Port**: `5432` (internal)
- **Database**: `claimsphere`
- **User**: `claimsphere`
- **Password**: `claimsphere123`

To change, edit `docker-compose.yml` and update:
- `POSTGRES_*` environment variables in `db` service
- `DATABASE_URL` in `backend` service

### Port Configuration

Default ports:
- **Backend**: `8000:8000`
- **Database**: `5432:5432` (exposed for local access)

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Host:Container
```

### OCR Configuration

To disable OCR (saves memory):
```bash
# In .env file
DISABLE_OCR=true
```

Or in `docker-compose.yml`:
```yaml
environment:
  DISABLE_OCR: "true"
```

## Development Workflow

### Hot-Reload Development

Use the development override file:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This enables:
- Code hot-reload (changes reflect immediately)
- Additional volume mounts
- Development-friendly settings

### Making Code Changes

1. Edit code in your local files
2. Changes are automatically reflected (with hot-reload)
3. Or restart: `docker-compose restart backend`

### Running Tests

```bash
# Run all tests
docker-compose exec backend pytest tests/

# Run specific test
docker-compose exec backend pytest tests/test_ocr.py

# With coverage
docker-compose exec backend pytest --cov=backend tests/
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Missing API keys → Add to `.env` file
- Port already in use → Change port in `docker-compose.yml`
- Database connection failed → Wait for db to be healthy

### Database Connection Errors

**Wait for database to be ready:**
```bash
docker-compose up db
# Wait for "database system is ready to accept connections"
```

**Check database health:**
```bash
docker-compose ps
# db service should show "healthy"
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### CAMEL-AI Not Working

**Check if CAMEL-AI is installed:**
```bash
docker-compose exec backend pip show camel-ai
```

**Check API key:**
```bash
docker-compose exec backend env | grep QIANFAN_API_KEY
```

**View agent initialization logs:**
```bash
docker-compose logs backend | grep -i "agent\|camel"
```

### OCR Not Working

**Check if OCR is disabled:**
```bash
docker-compose exec backend env | grep DISABLE_OCR
```

**Enable OCR:**
```bash
# In .env file
DISABLE_OCR=false
```

**Restart:**
```bash
docker-compose restart backend
```

### Out of Memory

**Disable OCR:**
```bash
# In .env
DISABLE_OCR=true
```

**Limit container memory:**
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### View Container Resources

```bash
# Resource usage
docker stats

# Specific container
docker stats claimsphere-backend
```

## Production Considerations

For production deployment:

1. **Change default passwords** in `docker-compose.yml`
2. **Use secrets management** (Docker secrets, AWS Secrets Manager, etc.)
3. **Set `DEBUG=False`**
4. **Use production database** (not containerized)
5. **Enable SSL/TLS**
6. **Set resource limits**
7. **Use multi-stage builds** for smaller images
8. **Enable health checks** and monitoring

## Clean Up

**Remove all containers and volumes:**
```bash
docker-compose down -v
```

**Remove images:**
```bash
docker-compose down --rmi all
```

**Full cleanup (⚠️ removes everything):**
```bash
docker-compose down -v --rmi all
docker system prune -a
```

## Next Steps

- See `docs/CAMEL_AI_SETUP.md` for CAMEL-AI configuration
- See `GETTING_STARTED.md` for general setup
- Visit http://localhost:8000/docs for API documentation
