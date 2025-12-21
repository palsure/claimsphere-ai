# Quick Start Guide

Get the Smart Expense Intelligence System running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Baidu AI Studio API credentials (get from https://aistudio.baidu.com)

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd ERNIE

# Install system dependency (poppler for PDF processing)
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies (includes PaddleOCR - may take a few minutes)
pip install -r requirements.txt
```

## Step 2: Configure API Keys

```bash
# Copy environment template
cp env.template .env

# Edit .env and add your credentials
# BAIDU_API_KEY=your_api_key_here
# BAIDU_SECRET_KEY=your_secret_key_here
```

Get your API keys from:
1. Go to https://aistudio.baidu.com
2. Sign up/Login
3. Navigate to API management
4. Create an API key and secret

## Step 3: Start Backend

```bash
# Start the FastAPI server
python backend/app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start Frontend (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
Ready on http://localhost:3000
```

## Step 5: Test the System

1. Open http://localhost:3000 in your browser
2. Upload a receipt (PDF, JPG, or PNG)
3. Watch it process with PaddleOCR and ERNIE
4. View the extracted expense information
5. Try the natural language query feature

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify Python dependencies are installed
- Check .env file has correct API keys

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### OCR not working
- Install poppler-utils: `sudo apt-get install poppler-utils` (Linux) or `brew install poppler` (Mac)
- Check PaddleOCR installation: `python -c "import paddleocr; print('OK')"`

### ERNIE API errors
- Verify API keys in .env file
- Check your Baidu AI Studio account has credits
- Ensure API keys have proper permissions

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [docs/API.md](docs/API.md) for API reference
- See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment
- Review [SUBMISSION.md](SUBMISSION.md) for challenge submission details

## Need Help?

- Check the documentation in the `docs/` folder
- Review error messages in the terminal
- Ensure all dependencies are properly installed

Happy coding! 🚀

