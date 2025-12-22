# Render Deployment Guide

Complete guide for deploying ClaimSphere AI Backend to Render platform.

## 🎯 Quick Reference

| Item | Value |
|------|-------|
| **Platform** | Render.com |
| **Service Type** | Web Service |
| **Runtime** | Python 3.10 |
| **Build Time** | ~5-10 minutes |
| **Free Tier** | ✅ Available (512MB RAM) |
| **Recommended Plan** | Starter ($7/month) for OCR support |
| **Database** | SQLite (default) or PostgreSQL (recommended) |
| **Region** | Oregon (US West) recommended |

## 📋 Table of Contents

- [Quick Reference](#-quick-reference)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Environment Variables](#environment-variables)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Database Setup](#database-setup-optional)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Advanced Configuration](#advanced-configuration)
- [Cost Considerations](#cost-considerations)

## Prerequisites

Before deploying, ensure you have:

1. ✅ **GitHub Repository**: 
   - Code pushed to GitHub/GitLab/Bitbucket
   - Repository is public or you have admin access

2. ✅ **Render Account**: 
   - Sign up at [render.com](https://render.com)
   - Free tier available (no credit card required initially)
   - Connect your GitHub account

3. ✅ **Baidu AI Studio API Key**: 
   - Sign up at [aistudio.baidu.com](https://aistudio.baidu.com)
   - Create an application
   - Copy your `BAIDU_API_KEY`
   - Note: `BAIDU_SECRET_KEY` is optional for basic features

4. ✅ **JWT Secret Key**:
   - Generate a secure random string (32+ characters)
   - Use: `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"`
   - Keep this secret and never commit to Git

5. ✅ **Frontend Deployed** (Optional but recommended):
   - Deploy frontend to Vercel first (see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md))
   - You'll need the Vercel URL for CORS configuration

## Quick Start

1. **Get Baidu AI API Key**:
   - Visit [aistudio.baidu.com](https://aistudio.baidu.com)
   - Sign up/login and create an application
   - Copy your API key

2. **Push code to GitHub**:
   ```bash
   git push origin main
   ```

3. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)

4. **Create Web Service** (Manual Method - Recommended):
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure service:
     - **Name**: `claimsphere-ai-backend` (or your preferred name)
     - **Region**: Oregon (or closest to you)
     - **Branch**: `main`
     - **Root Directory**: Leave empty (root of repo)
     - **Runtime**: Python 3
     - **Build Command**: `python -m pip install --upgrade pip && pip install -r requirements.txt`
     - **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300 --workers 1`
     - **Plan**: Free

5. **Set Required Environment Variables**:
   - `BAIDU_API_KEY`: Your Baidu API key
   - `JWT_SECRET_KEY`: Generate a random secret (e.g., `openssl rand -hex 32`)
   - `FRONTEND_URL`: Your frontend URL (add after frontend is deployed)

6. **Deploy**: Click "Create Web Service" - initial deployment takes 5-10 minutes

## Detailed Deployment Steps

### Step 1: Prepare Your Repository

Ensure your code is ready:

```bash
# Check that render.yaml exists
ls render.yaml

# Verify frontend/next.config.js has output: 'standalone'
grep "output" frontend/next.config.js

# Commit and push
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Visit [render.com](https://render.com)
2. Sign up with GitHub (recommended for easy integration)
3. Verify your email address

### Step 3: Create Backend Service

**Option A: Manual Setup (Recommended for better control)**

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. If not connected, authorize Render to access your GitHub
3. Select your repository (e.g., `yourusername/claimsphere-ai`)
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `claimsphere-ai-backend` |
| **Region** | Oregon (or closest) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | Python 3 |
| **Build Command** | `python -m pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300 --workers 1` |
| **Plan** | Free |

5. Click **"Advanced"** and add environment variables (see next step)

**Option B: Blueprint Deployment (Automated)**

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Select your repository
3. Render detects `render.yaml` and creates both backend and frontend services
4. Note: You'll still need to add required environment variables manually

### Step 4: Configure Backend Service

After services are created, configure the backend:

1. Click on **`claimsphere-ai-backend`** service
2. Go to **"Environment"** tab
3. Add these REQUIRED environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `BAIDU_API_KEY` | `your_api_key` | **REQUIRED**: Get from Baidu AI Studio (aistudio.baidu.com) |
| `JWT_SECRET_KEY` | `random-secret-here` | **REQUIRED**: Generate with `openssl rand -hex 32` |
| `FRONTEND_URL` | `https://your-app.vercel.app` | **REQUIRED**: Your Vercel frontend URL (for CORS) |
| `DATABASE_URL` | `postgresql://...` | Optional: Auto-set when Render PostgreSQL database is added |

**Note**: Variables already configured in `render.yaml`:
- `PYTHON_VERSION`: 3.10.0
- `DEBUG`: False
- `HOST`: 0.0.0.0
- `DISABLE_OCR`: true (saves memory on free tier)
- `PADDLEOCR_USE_LITE_MODEL`: True
- `OMP_NUM_THREADS`: 1
- `MKL_NUM_THREADS`: 1

4. Click **"Save Changes"**

### Step 5: Configure Frontend Service

1. Click on **`claimsphere-ai-frontend`** service
2. Go to **"Environment"** tab
3. Add this environment variable:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://claimsphere-ai-backend.onrender.com` | Backend API URL |
| `NODE_VERSION` | `18.17.0` | Already set in render.yaml |
| `PORT` | `3000` | Already set in render.yaml |

4. Click **"Save Changes"**

### Step 6: Initial Deployment

1. Both services will start deploying automatically
2. Monitor deployment in the **"Events"** tab
3. Wait for both services to show **"Live"** status
4. Note the service URLs:
   - Backend: `https://claimsphere-ai-backend.onrender.com`
   - Frontend: `https://claimsphere-ai-frontend.onrender.com`

### Step 7: Update Cross-Service URLs

After both services are live:

1. **Update Backend `FRONTEND_URL`**:
   - Go to backend service → Environment
   - Update `FRONTEND_URL` to: `https://claimsphere-ai-frontend.onrender.com`
   - Save and redeploy

2. **Update Frontend `NEXT_PUBLIC_API_URL`**:
   - Go to frontend service → Environment
   - Update `NEXT_PUBLIC_API_URL` to: `https://claimsphere-ai-backend.onrender.com`
   - Save and redeploy

3. **Redeploy both services**:
   - Go to each service dashboard
   - Click **"Manual Deploy"** → **"Deploy latest commit"**

## Environment Variables

### Backend Service Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BAIDU_API_KEY` | ✅ Yes | - | Baidu AI Studio API key (get from aistudio.baidu.com) |
| `BAIDU_SECRET_KEY` | ⚠️ Optional | - | Baidu AI Studio secret key (for advanced features) |
| `JWT_SECRET_KEY` | ✅ Yes | - | Secret key for JWT tokens (generate random 32+ char string) |
| `FRONTEND_URL` | ✅ Yes | - | Frontend URL for CORS (e.g., `https://your-app.vercel.app`) |
| `DATABASE_URL` | ⚠️ Optional | SQLite | PostgreSQL URL (auto-set when Render database added) |
| `DISABLE_OCR` | No | `true` | Set to `false` to enable PaddleOCR (requires paid plan) |
| `DEBUG` | No | `False` | Debug mode (set `True` for verbose logging) |
| `HOST` | No | `0.0.0.0` | Server host (already configured) |
| `PYTHON_VERSION` | No | `3.10.0` | Python version (already configured) |
| `PORT` | No | Auto | Server port (automatically set by Render) |
| `DISABLE_MODEL_SOURCE_CHECK` | No | `True` | Disable PaddlePaddle model source check |

### Frontend Service Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | - | Backend API URL |
| `NODE_VERSION` | No | `18.17.0` | Node.js version |
| `PORT` | No | `3000` | Server port |

## Post-Deployment Configuration

### Verify Deployment

1. **Test Backend Health**:
   ```bash
   curl https://your-service-name.onrender.com/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-01-15T10:30:00.123456",
     "version": "1.0.0"
   }
   ```

2. **Test Backend API Root**:
   ```bash
   curl https://your-service-name.onrender.com/
   ```
   Should return welcome message with API information

3. **Test API Documentation**:
   - Visit: `https://your-service-name.onrender.com/docs`
   - Should load interactive Swagger UI
   - Try the `/health` endpoint

4. **Test Authentication**:
   ```bash
   curl -X POST https://your-service-name.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
   ```
   Should return access token if demo users are seeded

5. **Test Frontend Connection**:
   - Visit your Vercel frontend URL
   - Try signing up or logging in
   - Verify frontend can communicate with backend

### API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `https://your-service-name.onrender.com/docs`
  - Interactive API testing interface
  - Try endpoints directly in the browser
  - View request/response schemas
  
- **ReDoc**: `https://your-service-name.onrender.com/redoc`
  - Alternative documentation format
  - Better for reading and reference

### Database Setup (Optional)

By default, the backend uses SQLite (file-based database), which works fine for development but **is not recommended for production** because Render's filesystem is ephemeral.

**To add PostgreSQL database (Recommended for Production):**

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `claimsphere-ai-db`
   - **Database**: `claimsphere`
   - **User**: `claimsphere_user`
   - **Region**: Same as your backend service
   - **Plan**: Free (1GB storage) or Starter ($7/month, 10GB)
3. Click **"Create Database"**
4. After database is created, copy the **Internal Database URL**
5. Go to your backend service → **Environment** tab
6. Add/Update variable:
   - Key: `DATABASE_URL`
   - Value: Paste the internal database URL
7. Save and redeploy backend

**Important**: The backend will automatically:
- Create all required tables on first startup
- Run database migrations
- Seed demo users (user@example.com, agent@example.com)

**To verify database connection:**
```bash
# Check backend logs after deployment
# Should see: "Database initialized successfully"
```

### CORS Configuration

The backend CORS is automatically configured based on the `FRONTEND_URL` environment variable. Make sure to set it correctly:

```bash
# In Render backend environment variables
FRONTEND_URL=https://your-app.vercel.app
```

The backend (`backend/app.py`) dynamically configures CORS origins:

```python
# CORS is configured to allow:
# 1. The URL specified in FRONTEND_URL env variable
# 2. http://localhost:3000 (for local development)
# 3. http://localhost:3001 (alternative local port)
```

**Important**: 
- Do NOT include trailing slashes in `FRONTEND_URL`
- Use the exact Vercel deployment URL
- After changing `FRONTEND_URL`, redeploy the backend service

## Troubleshooting

### Backend Issues

#### Build Fails

**Symptoms**: Build fails during `pip install`

**Solutions**:
- Check `requirements.txt` is in root directory
- Verify Python version (3.9.0)
- Review build logs for specific package errors
- Ensure all dependencies are listed in `requirements.txt`

#### Service Won't Start

**Symptoms**: Service shows "Failed" status

**Solutions**:
- Check environment variables are set
- Verify `BAIDU_API_KEY` and `BAIDU_SECRET_KEY` are correct
- Review service logs in Render dashboard
- Ensure `startCommand` in render.yaml is correct

#### Health Check Fails

**Symptoms**: Health endpoint returns error or 502/503

**Solutions**:
- **Check Service Status**: Ensure service shows "Live" in dashboard
- **View Logs**: Click "Logs" tab to see startup errors
- **Verify Environment Variables**: Missing required env vars will cause startup failure
  - `BAIDU_API_KEY` must be set
  - `JWT_SECRET_KEY` must be set
  - `FRONTEND_URL` must be set
- **Check Service is Not Sleeping**: Free tier services sleep after 15 minutes
- **Wait for Cold Start**: First request after sleep takes 30-60 seconds
- **Verify Build Succeeded**: Check "Events" tab for build errors

**Common Startup Errors:**
```
Error: BAIDU_API_KEY not set
→ Solution: Add BAIDU_API_KEY in environment variables

Error: JWT_SECRET_KEY not set  
→ Solution: Add JWT_SECRET_KEY in environment variables

Error: Port already in use
→ Solution: This shouldn't happen on Render, check logs

Error: Database connection failed
→ Solution: Check DATABASE_URL if using PostgreSQL
```

#### Service Sleeping (Free Tier)

**Symptoms**: First request takes 30-60 seconds

**Solutions**:
- This is normal for free tier - services sleep after 15 minutes of inactivity
- Services wake up automatically on first request
- Consider upgrading to paid plan ($7/month) for 24/7 availability
- Use a cron job or uptime monitor to ping `/health` endpoint every 10 minutes to keep service awake

**Memory Issues on Free Tier**

**Symptoms**: Service crashes with "Out of memory" error

**Solutions**:
- Free tier is limited to 512MB RAM
- OCR is disabled by default (`DISABLE_OCR=true`) to fit within this limit
- If you need OCR, upgrade to Starter plan ($7/month) with 512MB+ RAM
- PaddleOCR requires ~800MB-1GB RAM with full models
- Ensure `PADDLEOCR_USE_LITE_MODEL=true` if enabling OCR

### Frontend Issues

#### Build Fails

**Symptoms**: Build fails during `npm run build`

**Solutions**:
- Check `frontend/package.json` exists
- Verify Node.js version (18.17.0)
- Review build logs for specific errors
- Ensure all dependencies are in `package.json`

#### API Connection Errors

**Symptoms**: Frontend can't connect to backend

**Solutions**:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend URL is accessible
- Ensure CORS is configured on backend
- Check browser console for specific errors

#### Page Not Loading

**Symptoms**: Blank page or 404 error

**Solutions**:
- Verify `npm run build` completed successfully
- Check `NEXT_PUBLIC_API_URL` environment variable
- Review browser console for errors
- Ensure frontend service is "Live"

### Common Issues

#### Environment Variables Not Updating

**Solution**: After changing env vars, manually redeploy:
1. Go to service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

#### CORS Errors

**Solution**: 
1. Verify `FRONTEND_URL` in backend matches frontend URL exactly
2. Check backend CORS configuration
3. Ensure URLs include `https://` protocol

#### Build Timeout

**Solution**:
- Free tier has limited build time
- Consider upgrading to paid plan
- Optimize build process (remove unnecessary dependencies)

## Advanced Configuration

### Custom Domains

To use a custom domain:

1. Go to service dashboard → **"Settings"** → **"Custom Domains"**
2. Add your domain (e.g., `api.yourdomain.com`)
3. Follow DNS configuration instructions
4. Update environment variables with new domain
5. Redeploy services

### Environment-Specific Configurations

Create separate Render services for staging/production:

1. **Staging Service**:
   - Use `render-staging.yaml` (create if needed)
   - Set `DEBUG=True`
   - Use staging API keys

2. **Production Service**:
   - Use `render.yaml`
   - Set `DEBUG=False`
   - Use production API keys

### Monitoring and Alerts

1. **View Logs**:
   - Go to service dashboard → **"Logs"** tab
   - View real-time logs
   - Download logs for analysis

2. **Metrics**:
   - Monitor CPU, memory, and request metrics
   - View in service dashboard → **"Metrics"** tab

3. **Alerts**:
   - Set up email alerts for service failures
   - Configure in service dashboard → **"Alerts"**

### Auto-Deployment

Both services are configured with `autoDeploy: true`:

- Every push to `main` branch triggers deployment
- Both services deploy simultaneously
- Deployment status visible in dashboard

To disable auto-deploy:
1. Go to service dashboard → **"Settings"**
2. Toggle **"Auto-Deploy"** off

### Manual Deployment

To manually deploy:

1. Go to service dashboard
2. Click **"Manual Deploy"**
3. Select **"Deploy latest commit"** or specific commit
4. Monitor deployment in **"Events"** tab

## Service URLs

After deployment, your backend service will be available at:

- **Backend API**: `https://your-service-name.onrender.com`
- **API Documentation**: `https://your-service-name.onrender.com/docs`
- **Health Check**: `https://your-service-name.onrender.com/health`
- **API Root**: `https://your-service-name.onrender.com/` (shows welcome message)

**Note**: Replace `your-service-name` with your actual Render service name.

### Important URLs to Configure

1. **Backend `FRONTEND_URL`**: Set this to your Vercel frontend URL
   - Example: `https://claimsphere-ai.vercel.app`
   - Required for CORS to work properly

2. **Frontend `NEXT_PUBLIC_API_URL`**: Set this to your Render backend URL
   - Example: `https://your-service-name.onrender.com`
   - Required for frontend to communicate with backend

## Cost Considerations

### Free Tier (Perfect for Development & Demo)

**Included:**
- ✅ 512MB RAM per service
- ✅ Services sleep after 15 minutes of inactivity
- ✅ Shared CPU
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Free PostgreSQL database (90 days, then $7/month)

**Limitations:**
- ⚠️ First request after sleep takes 30-60 seconds (cold start)
- ⚠️ Not suitable for high-traffic production use
- ⚠️ OCR must be disabled due to memory constraints
- ⚠️ Limited build minutes per month

**Best for**: Development, testing, demos, proof-of-concept

### Starter Plan ($7/month per service)

**Included:**
- ✅ Services stay awake 24/7 (no cold starts)
- ✅ 512MB RAM (can enable OCR)
- ✅ 400 build hours/month
- ✅ Custom domains
- ✅ Priority support

**Best for**: Small production apps, personal projects, low-traffic websites

### Standard Plan ($25/month per service)

**Included:**
- ✅ 2GB RAM (full OCR support)
- ✅ 1 vCPU
- ✅ Everything from Starter
- ✅ Better performance

**Best for**: Production applications, higher traffic, resource-intensive features

### Recommendation for ClaimSphere AI

- **Demo/Testing**: Free tier (OCR disabled, SQLite database)
  - Perfect for hackathons, demos, proof-of-concept
  - Cold starts acceptable
  
- **Small Production**: Starter plan ($7/month, PostgreSQL free tier)
  - Can enable OCR with lite models
  - No cold starts
  - Good for personal projects, small teams
  
- **Full Production**: Standard plan ($25/month, PostgreSQL Starter $7/month)
  - Full OCR support
  - Better performance
  - Higher traffic capacity

**Total Cost Examples:**
- Free tier: $0/month (demo only)
- Production (basic): $7/month (web service only)
- Production (full): $32/month (web service + database + OCR)

## Security Best Practices

### Environment Variables Security

1. **Generate Strong JWT Secret**:
   ```bash
   # Generate a secure random secret
   openssl rand -hex 32
   # or
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Protect API Keys**:
   - Never commit API keys to Git
   - Only set them in Render environment variables
   - Rotate keys regularly

3. **CORS Configuration**:
   - Set `FRONTEND_URL` to your exact Vercel domain
   - Don't use wildcards (`*`) in production
   - Include protocol (`https://`)

4. **Database Security**:
   - Use Render's internal database URL (not external)
   - Enable SSL for PostgreSQL connections
   - Never expose database credentials

### Production Checklist

Before going live:

- [ ] `DEBUG=False` in environment variables
- [ ] Strong `JWT_SECRET_KEY` generated and set
- [ ] `FRONTEND_URL` set to production Vercel URL
- [ ] Database is PostgreSQL (not SQLite)
- [ ] CORS is properly configured
- [ ] API endpoints tested with production URLs
- [ ] Frontend can successfully connect to backend
- [ ] Health check returns 200 OK
- [ ] Demo users can log in
- [ ] File uploads work (if OCR enabled)

## Monitoring and Maintenance

### View Logs

Real-time logs are crucial for debugging:

1. Go to service dashboard
2. Click **"Logs"** tab
3. View live logs or filter by:
   - Date range
   - Log level (info, warning, error)
   - Search text

**Useful log searches:**
- `error` - Find all errors
- `startup` - Check initialization
- `health` - Monitor health checks
- `auth` - Debug authentication issues

### Monitor Performance

1. **Metrics Tab**:
   - CPU usage
   - Memory usage
   - Request latency
   - HTTP status codes

2. **Set Up Alerts**:
   - Go to service → **Settings** → **Alerts**
   - Enable email notifications for:
     - Service failures
     - High memory usage
     - Deployment failures

### Maintenance Tasks

**Weekly:**
- Check error logs for recurring issues
- Monitor memory usage (especially on free tier)
- Verify backups (if using PostgreSQL)

**Monthly:**
- Review and rotate API keys
- Update dependencies (`pip install --upgrade`)
- Check for security updates

**As Needed:**
- Scale up if hitting memory limits
- Upgrade to paid plan if cold starts are problematic
- Add custom domain for production

## Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
  - Web Services guide
  - Environment variables
  - Database setup
  
- **Render Status**: [status.render.com](https://status.render.com)
  - Check for platform-wide issues
  - Maintenance windows
  
- **Render Community**: [community.render.com](https://community.render.com)
  - Ask questions
  - Share solutions
  - Feature requests

- **ClaimSphere AI Documentation**:
  - [API Documentation](./API.md)
  - [Vercel Deployment](./VERCEL_DEPLOYMENT.md)
  - [General Deployment](./DEPLOYMENT.md)

## Common Deployment Scenarios

### Scenario 1: Quick Demo Deployment (Free Tier)

Perfect for hackathons, presentations, testing:

```bash
# 1. Get API key from Baidu AI Studio
# 2. Create Render Web Service
# 3. Set environment variables:
BAIDU_API_KEY=your_key_here
JWT_SECRET_KEY=random_secret_32_chars
FRONTEND_URL=https://your-app.vercel.app
# 4. Deploy - done!
```

**Characteristics:**
- ✅ Free
- ⚠️ Cold starts (30-60s)
- ⚠️ No OCR
- ⚠️ SQLite database (ephemeral)

### Scenario 2: Production Deployment (Paid)

For real applications with users:

```bash
# 1. Create Render PostgreSQL database
# 2. Create Render Web Service (Starter plan)
# 3. Set environment variables:
BAIDU_API_KEY=your_key_here
JWT_SECRET_KEY=random_secret_32_chars
FRONTEND_URL=https://your-app.vercel.app
DATABASE_URL=postgresql://...  # Auto-set
DISABLE_OCR=false  # Enable OCR
# 4. Deploy
```

**Characteristics:**
- ✅ Always online (no cold starts)
- ✅ OCR enabled
- ✅ Persistent PostgreSQL database
- ✅ Production-ready
- 💰 $7-32/month

### Scenario 3: Development/Staging Environment

For testing before production:

```bash
# Same as production but:
DEBUG=True
FRONTEND_URL=https://staging-app.vercel.app
# Use separate database
# Use separate API keys (if available)
```

## Next Steps

After successful deployment:

1. ✅ **Verify Deployment**:
   - Test health endpoint
   - Try API endpoints
   - Check logs for errors

2. ✅ **Configure Frontend**:
   - Deploy frontend to Vercel
   - Set `NEXT_PUBLIC_API_URL` to Render backend URL
   - Update `FRONTEND_URL` in backend

3. ✅ **Test End-to-End**:
   - Sign up new user
   - Submit a claim
   - Upload a document
   - Test natural language queries

4. ✅ **Set Up Monitoring** (Production):
   - Enable email alerts
   - Monitor logs regularly
   - Track error rates

5. ✅ **Optional Enhancements**:
   - Add custom domain
   - Set up CI/CD
   - Configure auto-scaling
   - Add database backups

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| 502 Bad Gateway | Service is starting/sleeping (wait 60s) |
| Build fails | Check requirements.txt, verify Python version |
| Health check fails | Check env vars (BAIDU_API_KEY, JWT_SECRET_KEY) |
| CORS error | Verify FRONTEND_URL matches Vercel URL exactly |
| Database error | Check DATABASE_URL or switch to SQLite |
| Out of memory | Ensure DISABLE_OCR=true on free tier |
| Can't login | Check JWT_SECRET_KEY is set |
| API returns 401 | Token expired or invalid, login again |

---

**Need Help?** Check the [Troubleshooting](#troubleshooting) section or [open an issue](https://github.com/yourusername/claimsphere-ai/issues) on GitHub.

