# Vercel Deployment - REQUIRED STEPS

## ⚠️ CRITICAL: This Cannot Be Done Via Code

The Root Directory setting **MUST** be configured in the Vercel Dashboard. It cannot be set via `vercel.json` or any code file.

---

## Step-by-Step Deployment

### Step 1: Delete Current Vercel Project (if exists)

If you already have a Vercel project that's failing:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **General** → scroll to bottom
4. Click **"Delete Project"**
5. Confirm deletion

### Step 2: Create New Project with Correct Configuration

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Select your Git repository
4. **IMPORTANT:** Before clicking Deploy:
   - Look for **"Root Directory"** section
   - Click **"Edit"** next to it
   - Enter: `frontend` (exactly, without quotes)
   - Click **"Continue"**

5. Verify auto-detected settings:
   - Framework Preset: **Next.js** (should auto-detect)
   - Build Command: **`npm run build`** or **`next build`**
   - Output Directory: **`.next`**
   - Install Command: Should be blank or **`npm install`**

6. Set Environment Variables:
   - Click **"Add Environment Variable"**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://claimsphere-ai-backend.onrender.com`
   - Select all environments (Production, Preview, Development)

7. Click **"Deploy"**

---

## Alternative: Update Existing Project

If you want to keep your existing project:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **"Settings"** → **"General"**
4. Find **"Root Directory"**
5. Click **"Edit"**
6. Enter: `frontend`
7. Click **"Save"**
8. Go to **"Environment Variables"** → Add if not present:
   - `NEXT_PUBLIC_API_URL` = `https://claimsphere-ai-backend.onrender.com`
9. Go to **"Deployments"** tab
10. Find the latest deployment → Click **"..."** menu
11. Click **"Redeploy"** → Check **"Use existing Build Cache"** = OFF
12. Click **"Redeploy"**

---

## Why This Works

With Root Directory set to `frontend`:

```
Your repo structure:
/
├── backend/          (ignored by Vercel)
├── frontend/         ← Vercel starts here
│   ├── package.json  ← Vercel detects Next.js from this
│   ├── src/
│   └── ...
└── ...
```

Vercel will:
- ✅ Detect Next.js correctly
- ✅ Install all dependencies automatically
- ✅ Build successfully
- ✅ Deploy to production

---

## Troubleshooting

### "Could not identify Next.js version"
→ Root Directory is not set to `frontend` in the dashboard

### "No package.json found"
→ Root Directory is incorrect or not set

### Build succeeds but page shows 404
→ Check Output Directory is `.next` (relative to Root Directory)

---

## Summary

**Do NOT use vercel.json or root package.json** - they are not needed and cause confusion.

**Do THIS instead:**
1. Set Root Directory to `frontend` in Vercel Dashboard
2. Add environment variable `NEXT_PUBLIC_API_URL`
3. Deploy

That's it! Vercel will auto-detect everything else.


