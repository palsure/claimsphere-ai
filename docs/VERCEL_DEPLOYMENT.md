# Vercel Deployment Guide

Deploy ClaimSphere AI frontend to Vercel.

## Prerequisites

1. GitHub repository with code
2. Vercel account ([vercel.com](https://vercel.com))
3. Backend deployed and URL available

## Quick Start

### 1. Import Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Connect GitHub and select your repository
4. **Important**: Set "Root Directory" to `frontend`
5. Vercel will auto-detect Next.js settings

### 2. Set Environment Variable

Add one environment variable:
- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: Your backend URL (e.g., `https://your-backend.onrender.com`)
- Select all environments (Production, Preview, Development)

### 3. Deploy

Click "Deploy". Deployment takes 1-2 minutes.

## Automatic Deployments

Vercel automatically redeploys when you push to GitHub:
- **Main branch** → Production deployment
- **Other branches** → Preview deployments
- Pull requests get unique preview URLs

## Verification

After deployment:
1. Visit your Vercel URL
2. Open browser DevTools Console (F12)
3. Look for: `API URL: https://your-backend.onrender.com`
4. Try signing up or logging in

## Troubleshooting

### "Could not identify Next.js version"
Root Directory not set to `frontend`. Fix:
1. Go to Settings → General → Root Directory
2. Set to `frontend`
3. Redeploy

### Build fails
- Check `package.json` exists in `frontend/` directory
- Verify all dependencies are listed
- Review build logs in Vercel dashboard

### Frontend can't connect to backend
- Check `NEXT_PUBLIC_API_URL` is set correctly
- No trailing slashes in URL
- Verify backend is accessible
- Check backend CORS configuration (must allow your Vercel domain)

### Signup/Login not working
1. Check browser console for errors
2. Check Network tab for failed requests
3. Verify `NEXT_PUBLIC_API_URL` is correct
4. Ensure backend `FRONTEND_URL` matches your Vercel URL

## Environment Variables

Required:
- `NEXT_PUBLIC_API_URL`: Backend API URL

Note: `NEXT_PUBLIC_` prefix makes the variable available in the browser.

## Manual Redeployment

To redeploy without code changes:
1. Go to Deployments tab
2. Find latest deployment
3. Click "..." → "Redeploy"
4. Uncheck "Use existing Build Cache" if changing environment variables

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
