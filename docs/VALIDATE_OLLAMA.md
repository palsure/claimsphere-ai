# How to Validate OLLAMA Private URL (http://ollama:11434)

Since `http://ollama:11434` is a private/internal URL, you need to test it from within Railway's network.

## Method 1: Test from Backend Service (Recommended)

### Using Railway CLI

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login and link to your project**:
   ```bash
   railway login
   railway link
   ```

3. **Test OLLAMA connection from backend service**:
   ```bash
   # Test if OLLAMA is reachable
   railway run --service claimsphere-ai curl http://ollama:11434/api/tags
   ```

   **Expected output:**
   ```json
   {
     "models": [
       {
         "name": "phi3:mini",
         "modified_at": "2026-01-13T...",
         "size": 2300000000,
         ...
       }
     ]
   }
   ```

4. **Test OLLAMA health check**:
   ```bash
   railway run --service claimsphere-ai curl http://ollama:11434/api/tags
   ```

5. **Test a simple completion** (if model is available):
   ```bash
   railway run --service claimsphere-ai curl -X POST http://ollama:11434/api/generate \
     -H "Content-Type: application/json" \
     -d '{"model": "phi3:mini", "prompt": "Hello", "stream": false}'
   ```

### Using Railway Web Terminal

1. Go to your **backend service** (`claimsphere-ai`) in Railway
2. Click on **"Deployments"** → **"View Logs"**
3. Click on **"Shell"** or **"Terminal"** tab
4. Run these commands:

   ```bash
   # Test OLLAMA connection
   curl http://ollama:11434/api/tags
   
   # If successful, you should see JSON with available models
   ```

## Method 2: Check Backend Logs

1. Go to your **backend service** in Railway
2. Click **"Deployments"** → **"View Logs"**
3. Look for OLLAMA-related log messages:

   **Success indicators:**
   ```
   ✅ Query Agent initialized with OLLAMA (phi3:mini) via CAMEL-AI
   Using CAMEL-AI Query Agent for query: ...
   CAMEL-AI query successful. Method: CAMEL-AI_ChatAgent_OLLAMA_phi3_mini
   ```

   **Error indicators:**
   ```
   ⚠️ OLLAMA not available at http://ollama:11434: ...
   OLLAMA returned status 500
   Connection refused
   ```

## Method 3: Test from Backend Code

Add a test endpoint to your backend to verify OLLAMA connectivity:

```python
# In backend/app.py or a test file
import requests
from fastapi import APIRouter

router = APIRouter()

@router.get("/test-ollama")
async def test_ollama():
    """Test OLLAMA connectivity"""
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    
    try:
        # Test 1: Check if OLLAMA is reachable
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                "status": "success",
                "ollama_url": ollama_url,
                "available_models": [m.get('name') for m in models],
                "phi3_mini_available": any('phi3:mini' in m.get('name', '') for m in models)
            }
        else:
            return {
                "status": "error",
                "message": f"OLLAMA returned status {response.status_code}",
                "response": response.text
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Cannot connect to OLLAMA",
            "ollama_url": ollama_url,
            "error": "Connection refused"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "ollama_url": ollama_url
        }
```

Then test it:
```bash
# From your local machine
curl https://your-backend.up.railway.app/test-ollama
```

## Method 4: Check Environment Variables

1. Go to your **backend service** in Railway
2. Click **"Variables"** tab
3. Verify these variables are set:
   ```
   USE_OLLAMA=true
   OLLAMA_BASE_URL=http://ollama:11434
   ```

## Troubleshooting

### Issue: Connection Refused

**Symptoms:**
```
ConnectionError: Cannot connect to OLLAMA
Connection refused
```

**Solutions:**
1. **Verify OLLAMA service is running:**
   - Go to OLLAMA service → Check status (should be "Online")
   - Check OLLAMA logs for errors

2. **Verify service names match:**
   - OLLAMA service name should be exactly `ollama` (case-sensitive)
   - Check in Railway: Service → Settings → General → Service Name

3. **Check if services are in same project:**
   - Both services must be in the same Railway project
   - Private networking only works within the same project

### Issue: Timeout

**Symptoms:**
```
TimeoutError: Request timed out
```

**Solutions:**
1. **Check OLLAMA is healthy:**
   ```bash
   railway run --service ollama curl http://localhost:11434/api/tags
   ```

2. **Increase timeout in backend code** (if needed)

### Issue: Model Not Found

**Symptoms:**
```
phi3:mini model not found in OLLAMA
```

**Solutions:**
1. **Pull the model:**
   ```bash
   railway run --service ollama ollama pull phi3:mini
   ```

2. **Verify model is available:**
   ```bash
   railway run --service ollama ollama list
   ```

### Issue: 404 Not Found

**Symptoms:**
```
404 Not Found
```

**Solutions:**
1. **Check OLLAMA port:**
   - Default port is `11434`
   - Verify in OLLAMA service settings

2. **Check URL format:**
   - Should be `http://ollama:11434` (not `https://`)
   - No trailing slash

## Quick Validation Checklist

- [ ] OLLAMA service is "Online" in Railway
- [ ] Backend service has `OLLAMA_BASE_URL=http://ollama:11434` set
- [ ] Backend service has `USE_OLLAMA=true` set
- [ ] Both services are in the same Railway project
- [ ] OLLAMA service name is exactly `ollama`
- [ ] `phi3:mini` model is pulled in OLLAMA
- [ ] `curl http://ollama:11434/api/tags` works from backend service
- [ ] Backend logs show successful OLLAMA initialization

## Expected Successful Response

When OLLAMA is working correctly, you should see:

**From `curl http://ollama:11434/api/tags`:**
```json
{
  "models": [
    {
      "name": "phi3:mini",
      "modified_at": "2026-01-13T12:00:00Z",
      "size": 2300000000,
      "digest": "sha256:...",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "phi",
        "parameter_size": "3.8B",
        "quantization_level": "Q4_0"
      }
    }
  ]
}
```

**From backend logs:**
```
✅ Query Agent initialized with OLLAMA (phi3:mini) via CAMEL-AI
Using CAMEL-AI Query Agent for query: ...
CAMEL-AI query successful. Method: CAMEL-AI_ChatAgent_OLLAMA_phi3_mini
```

## Next Steps

Once validated:
1. Test a real query through your API
2. Check that AI review is working
3. Monitor logs for any connection issues
4. Set up alerts if OLLAMA becomes unavailable
