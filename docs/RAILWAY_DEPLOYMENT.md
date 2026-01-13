# Railway Deployment Guide

This guide explains how to deploy OLLAMA and the backend to Railway.

## Overview

Railway allows you to deploy multiple services. We'll deploy:
1. **OLLAMA Service** - Local LLM server (phi3:mini)
2. **Backend Service** - FastAPI application
3. **PostgreSQL Database** - Railway's managed PostgreSQL (recommended)

## Prerequisites

- Railway account: https://railway.app
- GitHub repository with your code
- Railway CLI (optional): `npm i -g @railway/cli`

## Step 1: Create a New Railway Project

1. Go to https://railway.app and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

## Step 2: Deploy OLLAMA Service

### Option A: Deploy OLLAMA as a Service (Recommended)

1. In your Railway project, click **"+ New"** → **"Empty Service"**
2. Name it: `ollama`
3. Click on the service → **"Settings"** → **"Deploy"**
4. Configure the service:

**Settings:**
- **Source**: Connect to your GitHub repo
- **Root Directory**: Leave empty (or set to `/` if needed)
- **Build Command**: Leave empty (we'll use Docker)
- **Start Command**: Leave empty (Docker will handle it)

**Docker Configuration:**
Create a file `railway-ollama.json` in your repo root:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.ollama"
  }
}
```

Create `Dockerfile.ollama`:

```dockerfile
FROM ollama/ollama:latest

# Expose OLLAMA port
EXPOSE 11434

# OLLAMA runs automatically on port 11434
# No additional setup needed
```

**Environment Variables:**
- No environment variables needed for OLLAMA

**Deploy:**
- Railway will automatically detect the Dockerfile and deploy
- Wait for the service to start (may take 2-3 minutes)

**Get OLLAMA URL:**
- After deployment, go to **"Settings"** → **"Networking"**
- **For Private Networking (Recommended for same project):**
  - Use: `http://ollama:11434` (service name)
  - Or: `http://ollama.railway.internal:11434` (full internal domain)
  - No need to generate a public domain if services are in the same project
- **For Public Networking (if needed for external access):**
  - Click **"Generate Domain"** to create a public URL
  - Copy the **"Public Domain"** (e.g., `ollama-production.up.railway.app`)
  - Use: `https://ollama-production.up.railway.app`

### Option B: Use Railway's One-Click OLLAMA Template

1. In Railway, click **"+ New"** → **"Template"**
2. Search for "OLLAMA" or use: `https://github.com/railwayapp/templates/tree/main/ollama`
3. Deploy the template
4. Note the service URL

## Step 3: Pull phi3:mini Model into OLLAMA

After OLLAMA is deployed, you need to pull the model:

**Option 1: Using Railway CLI**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to OLLAMA service
railway run --service ollama ollama pull phi3:mini
```

**Option 2: Using Railway's Web Terminal**

1. Go to your OLLAMA service in Railway
2. Click **"Deployments"** → **"View Logs"**
3. Click **"Shell"** or **"Terminal"** tab
4. Run:
```bash
ollama pull phi3:mini
```

**Option 3: Using HTTP API (from your local machine)**

```bash
# Replace with your OLLAMA public URL
OLLAMA_URL="https://ollama-production.up.railway.app"

# Pull the model
curl -X POST "$OLLAMA_URL/api/pull" \
  -H "Content-Type: application/json" \
  -d '{"name": "phi3:mini"}'
```

**Verify Model is Available:**

```bash
# List models
curl "$OLLAMA_URL/api/tags"
```

You should see `phi3:mini` in the list.

## Step 4: Deploy PostgreSQL Database

1. In Railway project, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL instance
3. Go to **"Variables"** tab to see connection details:
   - `DATABASE_URL` (automatically set)
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

**Note:** Railway automatically sets `DATABASE_URL` for services in the same project.

## Step 5: Deploy Backend Service

1. In Railway project, click **"+ New"** → **"GitHub Repo"** (or **"Empty Service"**)
2. Name it: `backend`
3. Configure the service:

**Settings:**
- **Source**: Your GitHub repo
- **Root Directory**: `/` (root of repo)
- **Build Command**: Leave empty (Docker handles it)
- **Start Command**: Leave empty (Docker handles it)

**Docker Configuration:**
Railway will automatically detect your `Dockerfile` in the root.

**Environment Variables:**
Go to **"Variables"** tab and add:

```bash
# Database (Railway auto-provides this, but you can override)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Application
DEBUG=False
HOST=0.0.0.0
PORT=${{PORT}}
FRONTEND_URL=https://your-frontend-domain.vercel.app

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# OCR Configuration
DISABLE_MODEL_SOURCE_CHECK=True
DISABLE_OCR=false

# OLLAMA Configuration
USE_OLLAMA=true
# Use Railway's private networking (recommended for same project)
# Option 1: Service name (simplest)
OLLAMA_BASE_URL=http://ollama:11434
# Option 2: Full internal domain (also works)
# OLLAMA_BASE_URL=http://ollama.railway.internal:11434
# Option 3: Public URL (only if services are in different projects)
# OLLAMA_BASE_URL=https://ollama-production.up.railway.app

# OpenAI (optional fallback)
OPENAI_API_KEY=

# Baidu AI Studio (optional fallback)
BAIDU_API_KEY=
BAIDU_SECRET_KEY=

# Qianfan (optional)
QIANFAN_API_KEY=

# Validation
USE_AI_VALIDATION=true
USE_OLLAMA_FOR_QUERIES=true
```

**Important Notes:**
- `PORT` is automatically set by Railway (use `${{PORT}}`)
- `OLLAMA_BASE_URL` should be:
  - `http://ollama:11434` if OLLAMA is in the same Railway project (internal networking)
  - `https://ollama-production.up.railway.app` if OLLAMA is in a different project (public URL)
- Railway services in the same project can communicate via service names (e.g., `ollama:11434`)

**Deploy:**
- Railway will build and deploy automatically
- Check logs for any errors

## Step 6: Configure Service Dependencies

Railway automatically handles service dependencies within the same project. However, you can ensure the backend waits for OLLAMA:

1. Go to **Backend Service** → **"Settings"** → **"Deploy"**
2. Under **"Healthcheck"**, add:
   - **Path**: `/health`
   - **Port**: `${{PORT}}`

## Step 7: Run Database Migrations

After backend is deployed, run migrations:

**Option 1: Using Railway CLI**

```bash
railway run --service backend alembic upgrade head
```

**Option 2: Using Railway's Web Terminal**

1. Go to **Backend Service** → **"Deployments"** → **"View Logs"**
2. Click **"Shell"** tab
3. Run:
```bash
alembic upgrade head
```

## Step 8: Verify Deployment

### Check OLLAMA:
```bash
curl https://ollama-production.up.railway.app/api/tags
```

### Check Backend Health:
```bash
curl https://backend-production.up.railway.app/health
```

### Check Backend API:
```bash
curl https://backend-production.up.railway.app/api/health
```

## Step 9: Update Frontend Configuration

Update your frontend (Vercel) environment variables:

```bash
NEXT_PUBLIC_API_URL=https://backend-production.up.railway.app
```

## Troubleshooting

### OLLAMA Not Responding

1. **Check OLLAMA logs:**
   - Go to OLLAMA service → **"Deployments"** → **"View Logs"**
   - Look for errors

2. **Verify model is pulled:**
   ```bash
   curl https://ollama-production.up.railway.app/api/tags
   ```

3. **Check OLLAMA health:**
   ```bash
   curl https://ollama-production.up.railway.app/api/tags
   ```

### Backend Can't Connect to OLLAMA

1. **Check OLLAMA_BASE_URL:**
   - If services are in same project: `http://ollama:11434`
   - If services are in different projects: `https://ollama-production.up.railway.app`

2. **Check backend logs:**
   - Go to Backend service → **"Deployments"** → **"View Logs"**
   - Look for connection errors

3. **Test OLLAMA connectivity from backend:**
   ```bash
   # Method 1: Using Railway CLI
   railway run --service claimsphere-ai curl http://ollama:11434/api/tags
   
   # Method 2: Using test endpoint (after deployment)
   curl https://your-backend.up.railway.app/test-ollama
   ```
   
   **Expected response from test endpoint:**
   ```json
   {
     "ollama_enabled": true,
     "ollama_url": "http://ollama:11434",
     "status": "success",
     "message": "OLLAMA is reachable at http://ollama:11434",
     "available_models": ["phi3:mini"],
     "phi3_mini_available": true
   }
   ```

### Database Connection Issues

1. **Verify DATABASE_URL:**
   - Railway automatically provides `${{Postgres.DATABASE_URL}}`
   - Check in **"Variables"** tab

2. **Check database logs:**
   - Go to PostgreSQL service → **"Logs"**

### Build Failures

1. **Check build logs:**
   - Go to service → **"Deployments"** → **"View Logs"**
   - Look for Docker build errors

2. **Common issues:**
   - Missing dependencies in `requirements.txt`
   - Dockerfile syntax errors
   - Memory limits (Railway free tier has limits)

## Railway Service URLs

After deployment, Railway provides:
- **Public Domain**: `https://service-name-production.up.railway.app`
- **Internal Service Name**: `service-name` (for same-project communication)

## Cost Considerations

- **Railway Free Tier**: $5/month credit
- **OLLAMA**: Uses CPU/memory (no GPU on free tier)
- **PostgreSQL**: Included in free tier (limited storage)
- **Backend**: Uses compute resources

**Tips:**
- Use Railway's internal networking (`http://ollama:11434`) to avoid external traffic
- Monitor usage in Railway dashboard
- Consider upgrading if you need more resources

## Alternative: Single Service Deployment

If you want to deploy OLLAMA and backend together:

1. Create a single service
2. Use `docker-compose.yml` (Railway supports Docker Compose)
3. Configure all services in one deployment

However, **separate services are recommended** for:
- Better resource isolation
- Independent scaling
- Easier debugging
- Better cost management

## Next Steps

1. ✅ Deploy OLLAMA and pull phi3:mini
2. ✅ Deploy PostgreSQL database
3. ✅ Deploy backend with correct environment variables
4. ✅ Run database migrations
5. ✅ Verify all services are working
6. ✅ Update frontend API URL
7. ✅ Test the full application

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app
