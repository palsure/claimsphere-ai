# Render Deployment Guide

Complete guide for deploying ClaimSphere AI to Render platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Environment Variables](#environment-variables)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Prerequisites

Before deploying, ensure you have:

1. ✅ **GitHub Repository**: Code pushed to GitHub
2. ✅ **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
3. ✅ **Baidu AI Studio API Keys**: 
   - Get from [aistudio.baidu.com](https://aistudio.baidu.com)
   - You'll need `BAIDU_API_KEY` and `BAIDU_SECRET_KEY`

## Quick Start

1. **Push code to GitHub**:
   ```bash
   git push origin main
   ```

2. **Go to Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)

3. **Create Blueprint**:
   - Click "New +" → "Blueprint"
   - Connect GitHub repository
   - Render detects `render.yaml` automatically
   - Click "Apply"

4. **Set Environment Variables** (see [Environment Variables](#environment-variables) section)

5. **Deploy**: Services deploy automatically

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

### Step 3: Connect Repository

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. If not connected, authorize Render to access your GitHub
3. Select your repository: `palsure/claimsphere-ai` (or your repo)
4. Render will detect `render.yaml` and show a preview
5. Click **"Apply"** to create services

### Step 4: Configure Backend Service

After services are created, configure the backend:

1. Click on **`claimsphere-ai-backend`** service
2. Go to **"Environment"** tab
3. Add these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `BAIDU_API_KEY` | `your_api_key` | From Baidu AI Studio |
| `BAIDU_SECRET_KEY` | `your_secret_key` | From Baidu AI Studio |
| `FRONTEND_URL` | `https://claimsphere-ai-frontend.onrender.com` | Set after frontend deploys |
| `DEBUG` | `False` | Production mode |
| `HOST` | `0.0.0.0` | Already set in render.yaml |
| `PYTHON_VERSION` | `3.9.0` | Already set in render.yaml |

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
| `BAIDU_API_KEY` | ✅ Yes | - | Baidu AI Studio API key |
| `BAIDU_SECRET_KEY` | ✅ Yes | - | Baidu AI Studio secret key |
| `FRONTEND_URL` | ✅ Yes | - | Frontend URL for CORS |
| `DEBUG` | No | `False` | Debug mode |
| `HOST` | No | `0.0.0.0` | Server host |
| `PYTHON_VERSION` | No | `3.9.0` | Python version |
| `PORT` | No | Auto | Server port (set by Render) |

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
   curl https://claimsphere-ai-backend.onrender.com/health
   ```
   Expected: `{"status":"healthy","timestamp":"..."}`

2. **Test Backend API**:
   ```bash
   curl https://claimsphere-ai-backend.onrender.com/
   ```
   Should return API information

3. **Test Frontend**:
   - Visit: `https://claimsphere-ai-frontend.onrender.com`
   - Should load the application
   - Try uploading a claim document

### API Documentation

FastAPI automatically generates API documentation:

- **Swagger UI**: `https://claimsphere-ai-backend.onrender.com/docs`
- **ReDoc**: `https://claimsphere-ai-backend.onrender.com/redoc`

### CORS Configuration

The backend is configured to allow all origins in development. For production, update `backend/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claimsphere-ai-frontend.onrender.com",
        # Add other allowed origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

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

**Symptoms**: Health endpoint returns error

**Solutions**:
- Verify `/health` endpoint exists in `backend/app.py`
- Check service is not sleeping (free tier)
- Review service logs for errors
- Ensure service has started successfully

#### Service Sleeping (Free Tier)

**Symptoms**: First request takes 30-60 seconds

**Solutions**:
- This is normal for free tier
- Services wake up automatically on first request
- Consider upgrading to paid plan for 24/7 availability

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

After deployment, your services will be available at:

- **Backend API**: `https://claimsphere-ai-backend.onrender.com`
- **Frontend App**: `https://claimsphere-ai-frontend.onrender.com`
- **API Docs**: `https://claimsphere-ai-backend.onrender.com/docs`
- **Health Check**: `https://claimsphere-ai-backend.onrender.com/health`

## Cost Considerations

### Free Tier

- ✅ Services sleep after 15 minutes of inactivity
- ✅ Limited build time (~10 minutes)
- ✅ 512MB RAM per service
- ✅ Suitable for development and testing
- ⚠️ First request after sleep takes 30-60 seconds

### Paid Plans

Starting at $7/month per service:

- ✅ Services stay awake 24/7
- ✅ Faster builds
- ✅ More resources (RAM, CPU)
- ✅ Better for production workloads
- ✅ Custom domains included

## Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Status**: [status.render.com](https://status.render.com)
- **Community**: [community.render.com](https://community.render.com)

## Next Steps

After successful deployment:

1. ✅ Test all features end-to-end
2. ✅ Set up monitoring and alerts
3. ✅ Configure custom domain (optional)
4. ✅ Set up CI/CD for automated testing
5. ✅ Document API endpoints for users

