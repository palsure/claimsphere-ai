# Getting Started with ClaimSphere AI - Complete Guide

Get the Automated Claim Processing Agent running locally in minutes!

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [x] **Python 3.8+** installed (`python3 --version`)
- [x] **Node.js 16+** installed (`node --version`)
- [x] **poppler** for PDF processing
  - macOS: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`
- [x] **Baidu AI Studio API credentials** (get from [aistudio.baidu.com](https://aistudio.baidu.com))

---

## 🚀 Quick Start (Fastest Method)

### Option 1: Using Automated Scripts

**Terminal 1 - Start Backend:**
```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai
./start_backend_venv.sh
```

**Terminal 2 - Start Frontend:**
```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai
./start_frontend.sh
```

✅ **Done!** Your app is running at http://localhost:3000

---

## 📖 Detailed Setup (Step-by-Step)

### Step 1: Initial Setup

```bash
# Navigate to project directory
cd /Users/PalusS0502/Documents/hackathon/claimsphere-ai

# Install system dependency (poppler for PDF processing)
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils
```

### Step 2: Set Up Python Environment

**Create and activate virtual environment (recommended):**

```bash
# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies (includes PaddleOCR - may take a few minutes)
pip install -r requirements.txt
```

**Note:** PaddleOCR installation may take 5-10 minutes. If you encounter issues, you can start the server without it for testing, but document processing won't work.

### Step 3: Configure Environment Variables

```bash
# Copy environment template
cp env.template .env

# Edit .env file
nano .env  # or: open .env
```

**Add your Baidu AI Studio credentials:**
```env
BAIDU_API_KEY=your_api_key_here
BAIDU_SECRET_KEY=your_secret_key_here
```

**Get Your API Keys:**
1. Go to [https://aistudio.baidu.com](https://aistudio.baidu.com)
2. Sign up or log in
3. Navigate to API management
4. Create an API key and secret
5. Copy and paste them into your `.env` file

### Step 4: Start the Backend Server

**Option A: Using Python script (Recommended)**
```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai
python3 start_backend.py
```

**Option B: Using uvicorn directly**
```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai
python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Direct execution**
```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai
python backend/app.py
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 5: Start the Frontend Server (New Terminal)

**Open a new terminal window and run:**

```bash
cd /Users/<profile>/Documents/hackathon/claimsphere-ai/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**You should see:**
```
ready - started server on 0.0.0.0:3000
Ready on http://localhost:3000
```

---

## 🌐 Access the Application

Once both servers are running:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

---

## ✅ Verify Everything Works

### Test Backend Health

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-..."}

# Get API info
curl http://localhost:8000/

# Check API documentation
open http://localhost:8000/docs
```

### Test Frontend

1. Open http://localhost:3000 in your browser
2. Upload a sample claim document from the `samples/` folder
3. Watch it process with PaddleOCR and ClaimSphere AI
4. View the extracted claim information
5. Try the natural language query feature

---

## 🛠️ Troubleshooting

### Backend Issues

#### 1. Virtual environment not activating
```bash
source venv/bin/activate
which python  # Should show venv path like: /path/to/claimsphere-ai/venv/bin/python
```

#### 2. Dependencies not installing
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 4. Import errors
Make sure you're running from the project root directory:
```bash
cd /Users/PalusS0502/Documents/hackathon/claimsphere-ai
python3 start_backend.py
```

#### 5. Missing core dependencies
```bash
pip3 install fastapi uvicorn python-multipart python-dotenv pydantic
```

#### 6. PaddleOCR installation issues
```bash
# Install PaddleOCR separately
pip install paddlepaddle==2.6.2
pip install paddleocr==2.7.0

# Test installation
python -c "import paddleocr; print('PaddleOCR installed successfully!')"
```

**Note:** The app will work without PaddleOCR, but document processing features won't work. OCR initialization can be temporarily commented out for testing.

### Frontend Issues

#### 1. Node modules missing
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 2. Port 3000 already in use
```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### 3. Frontend can't connect to backend
- Check that backend is running: `curl http://localhost:8000/health`
- Verify `frontend/.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Check browser console for CORS errors

#### 4. Node.js version issues
```bash
# Check Node version (need 16+)
node --version

# Update if needed (using nvm):
nvm install 18
nvm use 18
```

### OCR Not Working

#### 1. Install poppler-utils
```bash
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Verify:
which pdfinfo  # Should show path to pdfinfo
```

#### 2. Check PaddleOCR installation
```bash
python -c "import paddleocr; print('OK')"
```

### ClaimSphere AI API Errors

#### 1. Verify API keys in .env file
```bash
cat .env | grep BAIDU
# Should show your API keys
```

#### 2. Check API key validity
- Go to https://aistudio.baidu.com
- Verify your account has credits
- Ensure API keys have proper permissions

#### 3. Test API connection
```bash
# From within Python
python3 -c "from backend.claimsphere_service import ClaimSphereService; print('ClaimSphere AI service OK')"
```

---

## 🛑 Stopping the Servers

### Option 1: Manual stop
Press `Ctrl+C` in each terminal window

### Option 2: Kill all processes
```bash
# Kill backend
pkill -f "uvicorn"

# Kill frontend
pkill -f "next dev"
```

### Option 3: Find and kill specific processes
```bash
# Find processes
ps aux | grep uvicorn
ps aux | grep "next dev"

# Kill by PID
kill -9 <PID>
```

---

## 📝 Common Workflows

### Fresh Start (Clean Installation)

```bash
# 1. Clean up previous installations
rm -rf venv
rm -rf frontend/node_modules
rm -rf frontend/.next

# 2. Recreate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Configure environment
cp env.template .env
nano .env  # Add your API keys

# 6. Start servers (in separate terminals)
python backend/app.py  # Terminal 1
cd frontend && npm run dev  # Terminal 2
```

### Restart After Code Changes

**Backend (supports hot-reload):**
- Changes are auto-detected if started with `--reload` flag
- Or press `Ctrl+C` and restart: `python backend/app.py`

**Frontend (supports hot-reload):**
- Changes are auto-detected by Next.js
- No restart needed for most changes

---

## 📚 Additional Information

### Project URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Backend Environment

- Uses **FastAPI** with **Uvicorn**
- Virtual environment isolates Python dependencies
- Supports hot-reload during development
- PaddleOCR for document text extraction
- ClaimSphere AI for AI processing

### Frontend Environment

- Built with **Next.js** and **React**
- Uses **npm** for package management
- Supports hot-reload during development
- TypeScript for type safety

---

## 🎯 Quick Test Checklist

After starting both servers, verify:

- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend loads: Visit http://localhost:3000
- [ ] Upload a sample document from `samples/` folder
- [ ] Check claim is processed and displayed
- [ ] Try the natural language query feature
- [ ] View analytics dashboard
- [ ] Check API documentation at http://localhost:8000/docs

---

## 📖 Next Steps

Once your app is running locally:

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Read the main README**: `cat README.md` for project overview
3. **Check API documentation**: `docs/API.md` for detailed API reference
4. **Learn about deployment**: `docs/DEPLOYMENT.md` for production deployment
5. **Review submission details**: `SUBMISSION.md` for challenge information
6. **Try sample documents**: Upload files from the `samples/` directory

---

## 💡 Tips & Best Practices

1. **Always activate virtual environment** before working with Python:
   ```bash
   source venv/bin/activate
   ```

2. **Use separate terminals** for backend and frontend to see logs clearly

3. **Check logs** when something goes wrong - they usually indicate the issue

4. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt  # Backend
   npm update  # Frontend
   ```

5. **Use hot-reload** - both servers auto-restart on code changes

6. **Test API endpoints** using the Swagger UI at http://localhost:8000/docs

---

## 🆘 Need Help?

- Check the documentation in the `docs/` folder
- Review error messages in the terminal (they're usually helpful!)
- Ensure all dependencies are properly installed
- Verify environment variables are correctly set
- Check that required system dependencies (poppler) are installed

---

## 🎉 Success!

Your ClaimSphere AI Automated Claim Processing Agent is now running locally!

**Next**: Try uploading a claim document and watch the AI process it automatically.

Happy coding! 🚀

