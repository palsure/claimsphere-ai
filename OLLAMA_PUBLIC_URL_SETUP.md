# Setting Up OLLAMA Public URL (Quick Fix)

Since private networking isn't working, we'll use OLLAMA's public URL.

## Step 1: Get OLLAMA Public URL

1. Go to your **OLLAMA service** in Railway
2. Click **"Settings"** tab
3. Click **"Networking"** section
4. Under **"Public Networking"**, click **"Generate Domain"**
5. Copy the generated URL (e.g., `ollama-production.up.railway.app`)

## Step 2: Update Backend Environment Variable

1. Go to your **backend service** (`claimsphere-ai` or `web`) in Railway
2. Click **"Variables"** tab
3. Find or add `OLLAMA_BASE_URL`
4. Set it to:
   ```
   OLLAMA_BASE_URL=https://ollama-production.up.railway.app
   ```
   (Replace with your actual OLLAMA public URL)
5. **Save** the variable

## Step 3: Redeploy Backend

1. Railway will automatically redeploy when you save the variable
2. Or manually trigger a redeploy from the **"Deployments"** tab

## Step 4: Test Connection

After redeploy, test:
```bash
curl https://web-production-636c8.up.railway.app/test-ollama
```

**Expected success:**
```json
{
  "status": "success",
  "message": "OLLAMA is reachable at https://ollama-production.up.railway.app",
  "phi3_mini_available": true
}
```

## Why This Works

- **Public URL**: Works across different Railway projects
- **HTTPS**: Secure connection
- **No DNS issues**: Public domain is always resolvable

## Security Note

Using a public URL means OLLAMA is accessible from the internet. However:
- OLLAMA doesn't require authentication by default
- Consider adding firewall rules if needed
- For production, you may want to add authentication

## Alternative: Check Service Names

If you want to use private networking, verify:

1. **OLLAMA service name** (Settings → General) must be exactly `ollama`
2. **Backend service name** doesn't matter
3. **Both services** must be in the **same Railway project**

If they're in different projects, public URL is the only option.
