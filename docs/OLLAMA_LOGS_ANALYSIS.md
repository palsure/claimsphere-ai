# OLLAMA Logs Analysis

## Understanding OLLAMA Startup Logs

### Successful Startup Indicators

When OLLAMA starts successfully, you'll see:

```
✅ Listening on [::]:11434 (version 0.13.5)
✅ starting runner
✅ entering low vram mode (CPU mode)
```

### Key Log Messages Explained

#### 1. Server Configuration
```
msg="server config" env="map[...OLLAMA_HOST:http://[::]:11434...]"
```
- **Meaning**: OLLAMA is configured to listen on port 11434
- **Status**: ✅ Normal

#### 2. Server Started
```
msg="Listening on [::]:11434 (version 0.13.5)"
```
- **Meaning**: OLLAMA server is running and ready to accept connections
- **Status**: ✅ **SUCCESS** - Server is up!

#### 3. GPU Detection
```
msg="discovering available GPUs..."
msg="inference compute" id=cpu library=cpu
```
- **Meaning**: No GPU detected, using CPU
- **Status**: ✅ Normal for Railway (CPU-only instances)
- **Note**: phi3:mini works fine on CPU, just slower

#### 4. Low VRAM Mode
```
msg="entering low vram mode" "total vram"="0 B" threshold="20.0 GiB"
```
- **Meaning**: No GPU VRAM available, using system RAM
- **Status**: ✅ Normal for CPU-only deployment
- **Impact**: Models run in CPU mode (slower but functional)

#### 5. Runner Started
```
msg="starting runner" cmd="/usr/bin/ollama runner --ollama-engine --port 34481"
```
- **Meaning**: OLLAMA runner process is ready
- **Status**: ✅ Normal

## What to Check Next

### 1. Verify OLLAMA is Accessible

**From Railway CLI:**
```bash
railway run --service ollama curl http://localhost:11434/api/tags
```

**From Backend Service:**
```bash
railway run --service claimsphere-ai curl http://ollama:11434/api/tags
```

**Expected Response:**
```json
{
  "models": []
}
```
(Empty if no models pulled yet)

### 2. Pull phi3:mini Model

Since OLLAMA is running, pull the model:

```bash
railway run --service ollama ollama pull phi3:mini
```

**Expected Output:**
```
pulling manifest
pulling 00e1317cbf74... 100% ▕████████████████▏ 2.3 GB
pulling 8934d96d3d34... 100% ▕████████████████▏ 1.0 KB
pulling 8c17c2e0d0e7... 100% ▕████████████████▏  48 KB
verifying sha256 digest
writing manifest
success
```

### 3. Verify Model is Available

```bash
railway run --service ollama ollama list
```

**Expected Output:**
```
NAME            ID              SIZE    MODIFIED
phi3:mini       8c17c2e0d0e7    2.3 GB  2 hours ago
```

### 4. Test from Backend

After pulling the model, test from your backend:

```bash
# Using test endpoint
curl https://your-backend.up.railway.app/test-ollama

# Expected response:
{
  "ollama_enabled": true,
  "ollama_url": "http://ollama:11434",
  "status": "success",
  "message": "OLLAMA is reachable at http://ollama:11434",
  "available_models": ["phi3:mini"],
  "phi3_mini_available": true
}
```

## Common Log Patterns

### ✅ Healthy Startup
```
Listening on [::]:11434
starting runner
inference compute id=cpu
entering low vram mode
```

### ⚠️ Warnings (Usually Safe)
- `experimental Vulkan support disabled` - Normal, Vulkan not needed
- `entering low vram mode` - Normal for CPU-only
- `total unused blobs removed: 0` - Normal, no cleanup needed

### ❌ Errors to Watch For
- `failed to start server` - Check port conflicts
- `connection refused` - Service not running
- `out of memory` - Need more RAM allocation

## Performance Expectations

### CPU Mode (Railway Free/Starter Tier)
- **Model Loading**: 10-30 seconds
- **First Response**: 5-15 seconds
- **Subsequent Responses**: 2-8 seconds
- **Memory Usage**: ~2-4 GB for phi3:mini

### GPU Mode (If Available)
- **Model Loading**: 2-5 seconds
- **First Response**: 1-3 seconds
- **Subsequent Responses**: 0.5-2 seconds
- **Memory Usage**: ~2 GB VRAM

## Next Steps

1. ✅ OLLAMA is running (confirmed by logs)
2. ⏭️ Pull phi3:mini model
3. ⏭️ Test connection from backend
4. ⏭️ Verify in backend logs

## Troubleshooting

### If OLLAMA stops responding:
1. Check Railway service status
2. Check logs for errors
3. Restart the service if needed

### If model pull fails:
1. Check disk space (need ~3GB for phi3:mini)
2. Check network connectivity
3. Try pulling again

### If backend can't connect:
1. Verify `OLLAMA_BASE_URL=http://ollama:11434` is set
2. Verify both services are in same project
3. Check backend logs for connection errors
