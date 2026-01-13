# Railway Quick Start Guide

## 🚀 Quick Deployment Steps

### 1. Deploy OLLAMA Service

1. **Create OLLAMA Service:**
   - Railway Dashboard → **"+ New"** → **"Empty Service"**
   - Name: `ollama`
   - Add Dockerfile (or use Railway's OLLAMA template)

2. **Pull phi3:mini Model:**
   ```bash
   # Using Railway CLI
   railway run --service ollama ollama pull phi3:mini
   
   # OR via HTTP API (replace with your OLLAMA URL)
   curl -X POST "https://ollama-production.up.railway.app/api/pull" \
     -H "Content-Type: application/json" \
     -d '{"name": "phi3:mini"}'
   ```

3. **Get OLLAMA URL (Private Networking - Recommended):**
   - Service → **"Settings"** → **"Networking"** → **"Private Networking"**
   - Use service name: `http://ollama:11434` (for services in same project)
   - Or full internal domain: `http://ollama.railway.internal:11434`
   - No public domain needed if using private networking

### 2. Deploy PostgreSQL Database

1. Railway Dashboard → **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway automatically provides `DATABASE_URL` environment variable

### 3. Deploy Backend Service

1. **Create Backend Service:**
   - Railway Dashboard → **"+ New"** → **"GitHub Repo"**
   - Select your repository
   - Name: `backend`

2. **Set Environment Variables:**
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   PORT=${{PORT}}
   USE_OLLAMA=true
   OLLAMA_BASE_URL=http://ollama:11434
   JWT_SECRET_KEY=your-secret-key
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

3. **Deploy:**
   - Railway auto-detects Dockerfile and deploys

4. **Run Migrations:**
   ```bash
   railway run --service backend alembic upgrade head
   ```

### 4. Verify Deployment

```bash
# Check Backend Health
curl https://your-backend.up.railway.app/health

# Test OLLAMA Connection (from backend)
curl https://your-backend.up.railway.app/test-ollama

# OR test directly from Railway CLI
railway run --service claimsphere-ai curl http://ollama:11434/api/tags
```

**Expected test-ollama response:**
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

## 🔧 Key Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Same project (private networking - recommended) |
| `OLLAMA_BASE_URL` | `http://ollama.railway.internal:11434` | Same project (full internal domain) |
| `OLLAMA_BASE_URL` | `https://ollama.up.railway.app` | Different project (public URL) |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Auto-provided by Railway |
| `PORT` | `${{PORT}}` | Auto-set by Railway |
| `USE_OLLAMA` | `true` | Enable OLLAMA |

## 📝 Important Notes

- **Internal Networking**: Services in same project can use `http://service-name:port`
- **Public URLs**: Use `https://service-name.up.railway.app` for external access
- **Model Size**: phi3:mini is ~2.3GB - ensure sufficient disk space
- **Memory**: OLLAMA needs ~4GB RAM for phi3:mini

## 🐛 Troubleshooting

**OLLAMA not responding?**
- Check logs: Service → **"Deployments"** → **"View Logs"**
- Verify model: `curl https://ollama.up.railway.app/api/tags`

**Backend can't connect to OLLAMA?**
- Check `OLLAMA_BASE_URL` environment variable
- Use internal URL if same project: `http://ollama:11434`
- Use public URL if different project: `https://ollama.up.railway.app`

**Database connection issues?**
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running

## 📚 Full Documentation

See [docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md) for detailed instructions.
