# Fix Railway Backend Environment Variables

## Problem
The backend test endpoint shows:
```json
"environment_variables": {
  "OLLAMA_BASE_URL": "NOT SET",
  "USE_OLLAMA": "NOT SET"
}
```

This means the backend cannot read the environment variables from Railway.

## Solution: Set Environment Variables in Railway

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Select your project
3. Click on your **backend service** (the one named "web" or "claimsphere-ai-backend")

### Step 2: Add Environment Variables
1. Click on the **"Variables"** tab
2. Click **"+ New Variable"** for each variable below

#### Variable 1: OLLAMA_BASE_URL
- **Name**: `OLLAMA_BASE_URL`
- **Value**: `https://ollama-production-4a7c.up.railway.app`
  - ⚠️ **Replace `4a7c` with YOUR actual OLLAMA service ID**
  - To find your OLLAMA URL:
    1. Go to OLLAMA service in Railway
    2. Click **Settings** → **Networking**
    3. Copy the public domain (should look like `https://ollama-production-XXXX.up.railway.app`)

#### Variable 2: USE_OLLAMA
- **Name**: `USE_OLLAMA`
- **Value**: `true`

### Step 3: Verify Variables Are Set
After adding, you should see:
```
OLLAMA_BASE_URL = https://ollama-production-4a7c.up.railway.app
USE_OLLAMA = true
```

### Step 4: **CRITICAL - Force Redeploy**
⚠️ **Railway does NOT automatically redeploy when you change environment variables!**

1. Go to **Deployments** tab
2. Click the **"Redeploy"** button (or three dots menu → Redeploy)
3. Wait for deployment to complete (usually 2-5 minutes)

### Step 5: Verify Variables Are Being Read
1. After redeploy completes, go to **Deployments** → Latest deployment → **View Logs**
2. Look for these lines at the very beginning:
   ```
   [STARTUP] OLLAMA_BASE_URL: https://ollama-production-4a7c.up.railway.app
   [STARTUP] USE_OLLAMA: true
   ```
3. If you see `NOT SET`, the variables aren't being read - check for typos

### Step 6: Test Connection
After redeploy, test the endpoint:
```bash
curl https://web-production-636c8.up.railway.app/test-ollama
```

Expected successful response:
```json
{
  "status": "success",
  "message": "OLLAMA is reachable at https://ollama-production-4a7c.up.railway.app",
  "phi3_mini_available": true,
  "environment_variables": {
    "OLLAMA_BASE_URL": "https://ollama-production-4a7c.up.railway.app",
    "USE_OLLAMA": "true"
  }
}
```

## Troubleshooting

### Still shows "NOT SET" after redeploy?
1. **Check for typos**: Variable names are case-sensitive
   - ✅ Correct: `OLLAMA_BASE_URL`
   - ❌ Wrong: `ollama_base_url`, `OLLAMA_BASE_URL_`, `OLLAMA_BASE_URL ` (trailing space)

2. **Verify you're setting in the correct service**:
   - Set variables in the **backend service** (not OLLAMA service)
   - Your backend service is named "web" (from the test response)

3. **Check Railway service name**:
   - The test shows `"railway_service": "web"`
   - Make sure you're editing the "web" service, not a different one

4. **Force a fresh redeploy**:
   - Sometimes Railway caches old configs
   - Try: Deployments → Three dots → "Redeploy" (not just "Restart")

### Connection still fails after variables are set?
1. **Verify OLLAMA URL is correct**:
   ```bash
   # Test from your local machine
   curl https://ollama-production-4a7c.up.railway.app/api/tags
   ```
   Should return JSON with models list

2. **Check OLLAMA service status**:
   - Go to OLLAMA service in Railway
   - Verify it shows "Online" status
   - Check logs for any errors

3. **Verify OLLAMA has the model**:
   - The response should show `phi3:mini` in available models
   - If not, pull it: `ollama pull phi3:mini` (from Railway OLLAMA service terminal)

## Quick Checklist

- [ ] Opened Railway dashboard
- [ ] Selected **backend service** (not OLLAMA)
- [ ] Added `OLLAMA_BASE_URL` with correct public URL
- [ ] Added `USE_OLLAMA=true`
- [ ] **Force redeployed** the backend service
- [ ] Checked startup logs show correct values (not "NOT SET")
- [ ] Tested `/test-ollama` endpoint returns success

## Next Steps After Success

Once `/test-ollama` returns success:
1. Test claim submission with AI review
2. Verify OLLAMA is being used in backend logs
3. Check that `phi3:mini` model is responding correctly
