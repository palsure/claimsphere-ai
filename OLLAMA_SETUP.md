# OLLAMA Setup for ClaimSphere AI

## ✅ Installation Complete!

OLLAMA has been successfully installed in Docker and integrated with CAMEL-AI.

## What Was Done

1. **Added OLLAMA service to `docker-compose.yml`**
   - Runs on port `11434`
   - Persistent volume for models
   - Health check configured

2. **Updated Agents to Support OLLAMA**
   - `ReviewAgent` - Checks OLLAMA first, then OpenAI, then Qianfan
   - `ApprovalAgent` - Same priority order
   - `RolePlayingCoordinator` - Uses OLLAMA for discussions

3. **Pulled Llama 3.2 Model**
   - Model: `llama3.2` (2GB, fast, good quality)
   - Ready to use immediately

## Model Priority Order

The agents now check models in this order:

1. **OLLAMA** (Free, Local) - `http://ollama:11434`
2. **OpenAI** (Cloud) - Requires `OPENAI_API_KEY`
3. **Qianfan** (Cloud) - Requires `QIANFAN_API_KEY`
4. **Fallback** - Basic rule-based processing

## Configuration

### Environment Variables

Add to your `.env` file (optional, defaults shown):

```bash
# OLLAMA Configuration (already set in docker-compose.yml)
OLLAMA_BASE_URL=http://ollama:11434  # For Docker network
# OLLAMA_BASE_URL=http://localhost:11434  # For local access
```

### Docker Compose

The OLLAMA service is already configured in `docker-compose.yml`:

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: claimsphere-ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
```

## Usage

### Start Services

```bash
# Start all services (including OLLAMA)
docker compose up -d

# Or start just OLLAMA
docker compose up -d ollama
```

### Pull Additional Models

```bash
# Pull a different model
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama pull qwen2.5
docker compose exec ollama ollama pull llama3.1
```

### List Available Models

```bash
docker compose exec ollama ollama list
```

### Test OLLAMA

```bash
# Test from within Docker network
docker compose exec backend curl http://ollama:11434/api/tags

# Test from host
curl http://localhost:11434/api/tags
```

## Model Recommendations

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama3.2** ✅ | 2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **Currently installed - Best balance** |
| mistral | 4GB | ⚡⚡ | ⭐⭐⭐⭐ | Good quality, multilingual |
| qwen2.5 | 4GB | ⚡⚡ | ⭐⭐⭐⭐ | Excellent for Chinese/English |
| llama3.1 | 4.7GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality, slower |

## Verify Integration

Check backend logs to confirm OLLAMA is being used:

```bash
docker compose logs backend | grep -i "ollama\|review agent\|approval agent"
```

You should see:
```
Review Agent initialized with OLLAMA (llama3.2) via CAMEL-AI
Approval Agent initialized with OLLAMA (llama3.2) via CAMEL-AI
```

## Troubleshooting

### OLLAMA Not Responding

```bash
# Check if OLLAMA is running
docker compose ps ollama

# Check logs
docker compose logs ollama

# Restart OLLAMA
docker compose restart ollama
```

### Model Not Found

```bash
# Pull the model again
docker compose exec ollama ollama pull llama3.2

# Verify model is available
docker compose exec ollama ollama list
```

### Backend Can't Connect

1. Check network: `docker compose exec backend ping ollama`
2. Check OLLAMA URL: Ensure `OLLAMA_BASE_URL=http://ollama:11434` in backend environment
3. Restart backend: `docker compose restart backend`

## Benefits

✅ **Completely Free** - No API keys needed  
✅ **Local Processing** - Data stays on your machine  
✅ **No Rate Limits** - Use as much as you want  
✅ **Privacy** - No data sent to external services  
✅ **Offline Capable** - Works without internet  

## Next Steps

1. **Test the integration**: Submit a claim and check if OLLAMA is used
2. **Monitor performance**: Check response times in logs
3. **Try different models**: Pull other models if needed
4. **Adjust temperature**: Modify agent code if you want different behavior

## Notes

- OLLAMA models are stored in Docker volume `ollama_data`
- Models persist across container restarts
- First request may be slower (model loading)
- GPU acceleration available if Docker has GPU access
