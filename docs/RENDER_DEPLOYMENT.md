# Render Deployment Guide

Deploy ClaimSphere AI backend to Render.com.

## Prerequisites

1. GitHub repository with code
2. Render account ([render.com](https://render.com))
3. Baidu AI Studio API key ([aistudio.baidu.com](https://aistudio.baidu.com))
4. JWT secret key (generate with `openssl rand -hex 32`)

## Quick Start

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `claimsphere-ai-backend`
   - **Region**: Oregon (or closest)
   - **Branch**: `main`
   - **Build Command**: `python -m pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 300 --workers 1`
   - **Plan**: Free

### 2. Set Environment Variables

Required variables:
- `BAIDU_API_KEY`: Your Baidu API key
- `JWT_SECRET_KEY`: Random secret (32+ characters)
- `FRONTEND_URL`: Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)

Optional variables (already configured in `render.yaml`):
- `PYTHON_VERSION`: 3.10.0
- `DEBUG`: False
- `DISABLE_OCR`: true (saves memory on free tier)

### 3. Deploy

Click "Create Web Service". Deployment takes 5-10 minutes.

## Verification

Test your deployment:

```bash
# Health check
curl https://your-service.onrender.com/health

# Login test
curl -X POST https://your-service.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `BAIDU_API_KEY` | Yes | Baidu AI Studio API key |
| `JWT_SECRET_KEY` | Yes | Secret for JWT tokens (32+ chars) |
| `FRONTEND_URL` | Yes | Frontend URL for CORS |
| `DATABASE_URL` | No | Auto-set when PostgreSQL database added |
| `DISABLE_OCR` | No | Default: true (free tier) |
| `DEBUG` | No | Default: False |

## Database Setup (Optional)

For production, use PostgreSQL instead of SQLite:

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Create database (free plan available)
3. Copy internal database URL
4. Add `DATABASE_URL` environment variable to backend service
5. Redeploy backend

## Troubleshooting

### Service Sleeping (Free Tier)
First request after 15 minutes takes 30-60 seconds. This is normal for free tier.

Solution: Upgrade to Starter plan ($7/month) for 24/7 availability.

### Build Fails
- Check `requirements.txt` exists
- Verify all dependencies are listed
- Check build logs in Render dashboard

### Health Check Fails
- Verify all required environment variables are set
- Check service logs for startup errors
- Wait 60 seconds if service was sleeping

### CORS Errors
- Verify `FRONTEND_URL` matches your Vercel URL exactly
- No trailing slashes
- Redeploy after changing environment variables

## Free Tier Limitations

- 512MB RAM (OCR must be disabled)
- Services sleep after 15 minutes
- 100GB bandwidth/month
- Cold start: 30-60 seconds

## Deployment Options

**Free Tier** ($0/month)
- Good for: demos, testing, proof-of-concept
- Limitations: cold starts, no OCR

**Starter Plan** ($7/month)
- Always-on service (no cold starts)
- 512MB RAM (can enable OCR with lite models)
- Custom domains

**Standard Plan** ($25/month)
- 2GB RAM (full OCR support)
- Better performance
- Higher traffic capacity

## Support

- [Render Documentation](https://render.com/docs)
- [Render Status](https://status.render.com)
- [Community Forum](https://community.render.com)
