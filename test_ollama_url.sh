#!/bin/bash
# Test script to verify OLLAMA URL is accessible

# Replace with your OLLAMA public URL from Railway
OLLAMA_URL="${OLLAMA_URL:-https://ollama-production.up.railway.app}"

echo "Testing OLLAMA at: $OLLAMA_URL"
echo ""

# Test 1: Check if OLLAMA is responding
echo "1. Testing OLLAMA health..."
if curl -s -f "$OLLAMA_URL/api/tags" > /dev/null; then
    echo "✅ OLLAMA is responding!"
else
    echo "❌ OLLAMA is not responding. Check your URL."
    exit 1
fi

# Test 2: List available models
echo ""
echo "2. Listing available models..."
MODELS=$(curl -s "$OLLAMA_URL/api/tags" | jq -r '.models[].name' 2>/dev/null || echo "")

if [ -z "$MODELS" ]; then
    echo "⚠️  No models found. You may need to pull phi3:mini:"
    echo "   curl -X POST \"$OLLAMA_URL/api/pull\" -H \"Content-Type: application/json\" -d '{\"name\": \"phi3:mini\"}'"
else
    echo "✅ Available models:"
    echo "$MODELS" | while read model; do
        echo "   - $model"
    done
    
    # Check if phi3:mini is available
    if echo "$MODELS" | grep -q "phi3:mini"; then
        echo ""
        echo "✅ phi3:mini is available!"
    else
        echo ""
        echo "⚠️  phi3:mini not found. Pull it with:"
        echo "   curl -X POST \"$OLLAMA_URL/api/pull\" -H \"Content-Type: application/json\" -d '{\"name\": \"phi3:mini\"}'"
    fi
fi

echo ""
echo "✅ OLLAMA URL test complete!"
echo ""
echo "For your backend, set:"
echo "  OLLAMA_BASE_URL=$OLLAMA_URL"
