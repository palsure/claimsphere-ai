# Debug Railway Environment Variables

## Problem
Environment variables are set in Railway but still showing as "NOT SET" in the backend.

## Enhanced Diagnostics

I've added better logging and a diagnostic endpoint to help debug this.

### Step 1: Commit and Push Changes

The enhanced startup script and diagnostic endpoint need to be deployed:

```bash
git add start.py backend/app.py
git commit -m "Add enhanced environment variable diagnostics"
git push
```

Railway will automatically redeploy when you push.

### Step 2: Check Startup Logs

After Railway redeploys, check the **Deploy Logs**:

1. Go to Railway → Your backend service → **Deployments** → Latest deployment → **Deploy Logs**
2. Look for these lines at the very beginning:
   ```
   ============================================================
   CLAIMSPHERE AI - STARTUP DIAGNOSTICS
   ============================================================
   Starting server on 0.0.0.0:8080
   PORT environment variable: 8080
   OLLAMA_BASE_URL: https://ollama-production-4a7c.up.railway.app
   USE_OLLAMA: true
   ============================================================
   ```

3. **If you see `NOT SET` in the logs:**
   - The variables are NOT being read by Railway
   - Check Railway Variables tab for typos
   - Verify you're editing the **correct service** (the "web" service)

### Step 3: Use Diagnostic Endpoint

After deployment, test the new diagnostic endpoint:

```bash
curl https://web-production-636c8.up.railway.app/env-check
```

This will show:
- All relevant environment variables
- Which variables Railway is providing
- Backend hostname and Railway metadata

**Expected output:**
```json
{
  "environment_variables": {
    "OLLAMA_BASE_URL": "https://ollama-production-4a7c.up.railway.app",
    "USE_OLLAMA": "true",
    ...
  },
  "all_env_keys": ["OLLAMA_BASE_URL", "USE_OLLAMA", ...]
}
```

### Step 4: Verify Variables in Railway

1. Go to Railway → Backend service → **Variables** tab
2. **Click the eye icon** next to each variable to reveal the value
3. Verify:
   - `OLLAMA_BASE_URL` = `https://ollama-production-4a7c.up.railway.app` (your actual URL)
   - `USE_OLLAMA` = `true` (exactly lowercase "true", not "True" or "TRUE")

### Step 5: Check Service Name

The test endpoint shows `"railway_service": "web"`. Make sure you're editing the **"web"** service, not a different service.

## Common Issues

### Issue: Variables show in Railway but not in logs
**Possible causes:**
1. **Wrong service**: You're editing a different service than the one running
2. **Not redeployed**: Railway hasn't redeployed after setting variables
3. **Typo in variable name**: Check for case sensitivity and spaces

**Fix:**
- Verify service name matches `"railway_service": "web"` from test endpoint
- Force redeploy: Deployments → Redeploy
- Double-check variable names (case-sensitive)

### Issue: Startup logs don't show diagnostic messages
**Possible causes:**
1. **Old deployment**: Logs are from before the code changes
2. **Different start command**: Railway might be using a different command

**Fix:**
- Wait for new deployment after pushing code changes
- Check `railway.json` has `"startCommand": "python start.py"`

### Issue: Variables are set but still "NOT SET" in endpoint
**Possible causes:**
1. **Service not redeployed**: Variables only take effect after redeploy
2. **Cached environment**: Old environment is still running

**Fix:**
- **Force redeploy**: Deployments → Three dots → Redeploy
- Wait 2-5 minutes for deployment to complete
- Test `/env-check` endpoint after redeploy

## Quick Verification Checklist

- [ ] Pushed code changes to trigger redeploy
- [ ] Checked Deploy Logs for `[STARTUP]` messages
- [ ] Verified variables in Railway Variables tab (click eye icon)
- [ ] Confirmed editing the "web" service (not OLLAMA service)
- [ ] Force redeployed after setting variables
- [ ] Tested `/env-check` endpoint
- [ ] Tested `/test-ollama` endpoint

## Next Steps

Once `/env-check` shows the variables correctly:
1. Test `/test-ollama` endpoint - should show `"status": "success"`
2. Test a claim submission with AI review
3. Check backend logs during claim processing to verify OLLAMA is being used
