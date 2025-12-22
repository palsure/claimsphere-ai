# Vercel Deployment Guide

Complete guide for deploying the frontend to Vercel with automatic rebuilds on each commit.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Automatic Deployments](#automatic-deployments)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. ✅ **GitHub Repository**: Code pushed to GitHub
2. ✅ **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (free tier available)
3. ✅ **Backend API URL**: Your backend should be deployed (e.g., on Render)

## Initial Setup

### Step 1: Connect Your GitHub Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. If not connected, click **"Connect Git Provider"** and authorize Vercel to access your GitHub
5. Select your repository: `palsure/claimsphere-ai` (or your repo name)
6. Click **"Import"**

### Step 2: Configure Project Settings

**IMPORTANT**: You must set the Root Directory before Vercel can detect Next.js!

1. **Root Directory**: **CRITICAL** - Set to `frontend` 
   - This tells Vercel where your Next.js app is located
   - Without this, Vercel will look in the root directory and won't find Next.js
   - This setting is in the project import screen or Settings → General

2. **Framework Preset**: Should auto-detect as "Next.js" after Root Directory is set
3. **Build Command**: `npm run build` (auto-detected)
4. **Output Directory**: `.next` (auto-detected)
5. **Install Command**: `npm install` (auto-detected)

**Note**: The `vercel.json` file is configured for when Root Directory is set to `frontend`. The commands in vercel.json are relative to the Root Directory.

### Step 3: Set Environment Variables

Before deploying, set environment variables:

1. In the project setup page, scroll to **"Environment Variables"**
2. Add the following variable:

   | Variable | Value | Description |
   |----------|-------|-------------|
   | `NEXT_PUBLIC_API_URL` | `https://claimsphere-ai-backend.onrender.com` | Your backend API URL |

3. Click **"Deploy"**

## Automatic Deployments

Vercel automatically deploys on every commit when you connect a Git repository. Here's how it works:

### How Automatic Deployments Work

1. **Push to GitHub**: When you push code to your connected branch
2. **Vercel Detects**: Vercel automatically detects the push via webhook
3. **Builds & Deploys**: Vercel builds and deploys your application
4. **Preview URLs**: Each commit gets a unique preview URL
5. **Production**: Pushes to `main`/`master` branch deploy to production

### Enable Automatic Deployments

Automatic deployments are **enabled by default** when you connect a Git repository. To verify:

1. Go to your project in [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Go to **"Settings"** → **"Git"**
4. Ensure **"Automatic deployments from Git"** is enabled

### Deployment Branches

By default, Vercel deploys:
- **Production**: `main` or `master` branch
- **Preview**: All other branches and pull requests

To change production branch:

1. Go to **"Settings"** → **"Git"**
2. Under **"Production Branch"**, select your branch (e.g., `main`)
3. Click **"Save"**

### Preview Deployments

Every commit to non-production branches creates a preview deployment:

- **Preview URL**: `https://your-project-{hash}.vercel.app`
- **Pull Request**: Automatically creates preview for PRs
- **Comments**: Vercel comments on PRs with deployment status

## Environment Variables

### Setting Environment Variables

1. Go to project → **"Settings"** → **"Environment Variables"**
2. Add variables for different environments:

   | Variable | Production | Preview | Development |
   |----------|-----------|---------|-------------|
   | `NEXT_PUBLIC_API_URL` | `https://claimsphere-ai-backend.onrender.com` | `https://claimsphere-ai-backend.onrender.com` | `http://localhost:8000` |

3. Click **"Save"**

### Environment-Specific Variables

- **Production**: Used for `main`/`master` branch deployments
- **Preview**: Used for branch and PR deployments
- **Development**: Used for `vercel dev` local development

## Deployment Workflow

### Standard Workflow

```bash
# 1. Make changes to your code
git add .
git commit -m "Update feature"

# 2. Push to GitHub
git push origin main

# 3. Vercel automatically:
#    - Detects the push
#    - Builds your application
#    - Deploys to production (if main branch)
#    - Creates preview (if other branch)
```

### Manual Deployment

To manually trigger a deployment:

1. Go to project → **"Deployments"** tab
2. Click **"Redeploy"** on any deployment
3. Or use Vercel CLI:
   ```bash
   vercel --prod
   ```

## Configuration Files

### vercel.json

The project includes a `vercel.json` in the root:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install",
  "rootDirectory": "frontend",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://claimsphere-ai-backend.onrender.com"
  }
}
```

This configuration:
- Sets `rootDirectory` to `frontend` (so Vercel knows where your Next.js app is)
- Defines build commands
- Sets default environment variables

### next.config.js

Located in `frontend/next.config.js`:

```javascript
const nextConfig = {
  reactStrictMode: true,
  // output: 'standalone' is commented out for Vercel
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};
```

## Troubleshooting

### Deployments Not Triggering

**Issue**: Pushes to GitHub don't trigger deployments

**Solutions**:
1. Check Git integration in **"Settings"** → **"Git"**
2. Verify webhook is active (should show recent events)
3. Reconnect repository if needed
4. Check GitHub repository settings → Webhooks

### Build Failures

**Issue**: Build fails during deployment

**Solutions**:
1. Check build logs in Vercel dashboard
2. Verify `rootDirectory` is correct in `vercel.json`
3. Ensure `package.json` is in the `frontend` directory
4. Check Node.js version compatibility

### Environment Variables Not Working

**Issue**: Environment variables not available in build

**Solutions**:
1. Ensure variables are set in Vercel dashboard
2. Variables starting with `NEXT_PUBLIC_` are available at build time
3. Redeploy after adding new variables
4. Check variable names match exactly (case-sensitive)

### Preview URLs Not Working

**Issue**: Preview deployments fail or don't work

**Solutions**:
1. Check build logs for errors
2. Verify environment variables are set for "Preview" environment
3. Ensure backend CORS allows preview URLs
4. Check API URL in preview environment variables

## Advanced Configuration

### Custom Domains

To add a custom domain:

1. Go to **"Settings"** → **"Domains"**
2. Add your domain (e.g., `app.yourdomain.com`)
3. Follow DNS configuration instructions
4. Vercel automatically provisions SSL certificate

### Deployment Hooks

To trigger external services on deployment:

1. Go to **"Settings"** → **"Git"** → **"Deploy Hooks"**
2. Create a deploy hook
3. Use the webhook URL to trigger external services

### Ignoring Deployments

To prevent deployments for certain commits:

1. Add `[skip vercel]` or `[vercel skip]` to commit message
2. Or configure in **"Settings"** → **"Git"** → **"Ignored Build Step"**

### Branch Protection

To require manual approval for production:

1. Go to **"Settings"** → **"Git"**
2. Enable **"Production Branch Protection"**
3. Deployments to production require manual approval

## Monitoring

### View Deployments

1. Go to project → **"Deployments"** tab
2. See all deployments with:
   - Status (Ready, Building, Error)
   - Commit message and author
   - Build time
   - Preview URLs

### View Logs

1. Click on any deployment
2. View **"Build Logs"** and **"Function Logs"**
3. Download logs for analysis

### Analytics

Vercel provides analytics for:
- Page views
- Performance metrics
- Real user monitoring
- Web Vitals

Enable in **"Analytics"** tab (may require paid plan)

## Best Practices

1. **Use Preview Deployments**: Test changes in preview before merging to main
2. **Set Environment Variables**: Use different API URLs for preview vs production
3. **Monitor Build Times**: Optimize if builds take too long
4. **Review Build Logs**: Check logs after each deployment
5. **Use Branch Protection**: Require approval for production deployments
6. **Keep Dependencies Updated**: Regularly update npm packages

## Quick Reference

### Vercel CLI

Install Vercel CLI:
```bash
npm i -g vercel
```

Login:
```bash
vercel login
```

Deploy:
```bash
vercel --prod
```

Link project:
```bash
vercel link
```

View deployments:
```bash
vercel ls
```

### Useful URLs

- **Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)
- **Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Status**: [vercel-status.com](https://vercel-status.com)

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Support**: Available in Vercel dashboard

