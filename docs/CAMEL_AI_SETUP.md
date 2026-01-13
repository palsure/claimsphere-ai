# CAMEL-AI Setup Guide for ClaimSphere AI

This guide explains how to set up CAMEL-AI framework for the multi-agent system in ClaimSphere AI.

## Prerequisites

- Python >= 3.10 and <= 3.14
- Baidu account (for Qianfan API access)

## Installation

### 1. Install CAMEL-AI

We recommend the full installation with all features:

```bash
pip install 'camel-ai[all]'
```

This includes:
- All model platforms (OpenAI, Google, Qianfan, etc.)
- RAG capabilities
- Document tools
- Web tools
- And more

### 2. Verify Installation

```bash
pip show camel-ai
```

You should see the installed version and dependencies.

## API Key Configuration

### Getting Your Qianfan API Key

Qianfan Platform provides access to ERNIE models (ERNIE 5.0 Thinking, ERNIE 4.5 VL) through CAMEL-AI.

#### Step-by-Step Guide:

1. **Visit Qianfan Console**
   - Go to: https://console.bce.baidu.com/qianfan/overview
   - Sign in with your Baidu account (create one if needed)

2. **Navigate to API Key Management**
   - Click on "Access Key" or "API Key" in the dashboard
   - Or go directly to: https://console.bce.baidu.com/iam/#/iam/accesskey

3. **Create or View API Key**
   - If you don't have an API key, click "Create Access Key"
   - Copy the API Key (it looks like: `ak-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Important**: Save it securely - you won't be able to view it again!

4. **Set Up Environment Variable**

   **Option A: Using .env file (Recommended)**
   
   Create or edit `.env` file in the project root:
   ```bash
   QIANFAN_API_KEY=ak-your-api-key-here
   ```
   
   The `.env` file is automatically loaded by the application.

   **Option B: Using Environment Variables**
   
   **For Bash (Linux, macOS, Git Bash):**
   ```bash
   export QIANFAN_API_KEY=ak-your-api-key-here
   ```
   
   **For Windows Command Prompt:**
   ```cmd
   set QIANFAN_API_KEY=ak-your-api-key-here
   ```
   
   **For Windows PowerShell:**
   ```powershell
   $env:QIANFAN_API_KEY="ak-your-api-key-here"
   ```

### Alternative: Baidu AI Studio API Keys

If you prefer to use direct Baidu AI Studio API (fallback mode), you can also set:

```bash
BAIDU_API_KEY=your-api-key
BAIDU_SECRET_KEY=your-secret-key
```

Get these from: https://aistudio.baidu.com

**Note**: The system will use CAMEL-AI with Qianfan if `QIANFAN_API_KEY` is set, otherwise it falls back to direct Baidu AI Studio API.

## Configuration

### Default Model Configuration

CAMEL-AI uses environment variables for default model configuration. For Qianfan/ERNIE models, we configure them in code, but you can set defaults:

```bash
# Optional: Set default model platform
export DEFAULT_MODEL_PLATFORM_TYPE=qianfan

# Optional: Set default model type
export DEFAULT_MODEL_TYPE=ernie-5.0-thinking
```

### Load Environment Variables in Python

The application automatically loads `.env` file using `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # Already done in app.py
```

## Testing Your Setup

### 1. Verify CAMEL-AI Installation

```python
python -c "import camel; print(camel.__version__)"
```

### 2. Test Agent Initialization

Run the application and check logs for:

```
[INFO] Extraction Agent initialized with ERNIE 5.0 Thinking
[INFO] Validation Agent initialized with ERNIE 5.0 Thinking
[INFO] Query Agent initialized with ERNIE 5.0 Thinking
```

If you see warnings like:
```
[WARNING] QIANFAN_API_KEY not set. Extraction Agent will use fallback.
```

This means the API key is not configured correctly. Check your `.env` file or environment variables.

### 3. Test a Claim Upload

1. Start the backend server:
   ```bash
   python -m uvicorn backend.app:app --reload
   ```

2. Upload a claim document through the API or frontend

3. Check the logs for agent activity:
   ```
   [INFO] Agent Extraction: extraction_started
   [INFO] Agent Validation: validation_started
   ```

## Multi-Agent System Architecture

The ClaimSphere AI multi-agent system consists of:

1. **OCR Agent** - Document processing (PaddleOCR)
2. **Extraction Agent** - Structured data extraction (ERNIE 5.0 Thinking)
3. **Validation Agent** - Claim validation (ERNIE 5.0 Thinking)
4. **Fraud Detection Agent** - Risk assessment (ERNIE 5.0 Thinking)
5. **Duplicate Agent** - Duplicate detection
6. **Query Agent** - Natural language queries (ERNIE 5.0 Thinking)
7. **Analytics Agent** - Insights generation (ERNIE 5.0 Thinking)
8. **Orchestrator Agent** - Coordinates workflows

All agents are initialized automatically when the application starts.

## Troubleshooting

### Issue: "CAMEL-AI not available"

**Solution**: Make sure CAMEL-AI is installed:
```bash
pip install 'camel-ai[all]'
```

### Issue: "QIANFAN_API_KEY not set"

**Solution**: 
1. Check your `.env` file exists and contains `QIANFAN_API_KEY=...`
2. Verify the API key is correct (starts with `ak-`)
3. Make sure you're in the project root directory when running the app

### Issue: "Failed to initialize CAMEL-AI agent"

**Possible causes**:
- Invalid API key
- Network connectivity issues
- API quota exceeded

**Solution**:
1. Verify API key at Qianfan console
2. Check network connection
3. Verify API quota/balance

### Issue: Agents using fallback mode

If agents fall back to direct ERNIE API:
- Check that `QIANFAN_API_KEY` is set correctly
- Verify CAMEL-AI is installed: `pip show camel-ai`
- Check application logs for specific error messages

## Next Steps

- Explore the agent workflows in `backend/agents/workflows.py`
- Customize agent system prompts in individual agent files
- Add new agents by extending `BaseAgent` class
- Review CAMEL-AI documentation: https://www.camel-ai.org

## Additional Resources

- CAMEL-AI Official Docs: https://www.camel-ai.org
- Qianfan Console: https://console.bce.baidu.com/qianfan/overview
- CAMEL-AI GitHub: https://github.com/camel-ai/camel
- ERNIE Model Examples: https://github.com/camel-ai/camel/blob/master/examples/models/ernie_model_example.py
