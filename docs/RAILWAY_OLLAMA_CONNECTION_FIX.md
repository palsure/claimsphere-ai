# Fixing OLLAMA Connection Issues on Railway

## Error: "Failed to resolve 'ollama'"

If you see this error:
```
NameResolutionError: Failed to resolve 'ollama' ([Errno -2] Name or service not known)
```

This means Railway's private networking cannot resolve the service name.

## Solutions (Try in Order)

### Solution 1: Use Full Internal Domain

1. Go to your **backend service** in Railway
2. Click **"Variables"** tab
3. Update `OLLAMA_BASE_URL`:
   ```
   OLLAMA_BASE_URL=http://ollama.railway.internal:11434
   ```
4. Redeploy the service

### Solution 2: Verify Service Names Match

1. Go to **OLLAMA service** → **Settings** → **General**
2. Check the **Service Name** (must be exactly `ollama` - case-sensitive)
3. If different, either:
   - Rename the service to `ollama`, OR
   - Update `OLLAMA_BASE_URL` to match the actual service name

### Solution 3: Verify Services Are in Same Project

1. Check that both `ollama` and `claimsphere-ai` services are in the **same Railway project**
2. Private networking only works within the same project
3. If they're in different projects, use Solution 4

### Solution 4: Use Public URL (Different Projects)

If services are in **different Railway projects**:

1. Go to **OLLAMA service** → **Settings** → **Networking**
2. Click **"Generate Domain"** to create a public URL
3. Copy the public domain (e.g., `ollama-production.up.railway.app`)
4. Go to **backend service** → **Variables**
5. Set:
   ```
   OLLAMA_BASE_URL=https://ollama-production.up.railway.app
   ```
6. Redeploy

### Solution 5: Check Railway Private Networking

1. Go to **OLLAMA service** → **Settings** → **Networking**
2. Under **"Private Networking"**, verify it shows:
   - `ollama.railway.internal` with IPv4 & IPv6
   - "Ready to talk privately · You can also simply call me ollama"
3. If not showing, Railway's private networking may not be enabled

## Testing the Fix

After updating the environment variable:

1. **Redeploy** your backend service
2. **Test** the connection:
   ```bash
   curl https://your-backend.up.railway.app/test-ollama
   ```

3. **Expected success response:**
   ```json
   {
     "status": "success",
     "message": "OLLAMA is reachable at http://ollama.railway.internal:11434",
     "phi3_mini_available": true
   }
   ```

## Quick Checklist

- [ ] Both services in same Railway project?
- [ ] OLLAMA service name is exactly `ollama`?
- [ ] `OLLAMA_BASE_URL` set correctly?
- [ ] Tried `http://ollama.railway.internal:11434`?
- [ ] OLLAMA service is "Online"?
- [ ] Backend service redeployed after env var change?

## Common Issues

### Issue: "Name or service not known"
**Fix**: Use `http://ollama.railway.internal:11434` instead of `http://ollama:11434`

### Issue: Services in different projects
**Fix**: Use OLLAMA's public URL from Settings → Networking

### Issue: Service name mismatch
**Fix**: Either rename service to `ollama` or update `OLLAMA_BASE_URL` to match actual name

## Next Steps

Once connection works:
1. Pull phi3:mini model: `railway run --service ollama ollama pull phi3:mini`
2. Verify model: `railway run --service ollama ollama list`
3. Test from backend: `curl https://your-backend.up.railway.app/test-ollama`
