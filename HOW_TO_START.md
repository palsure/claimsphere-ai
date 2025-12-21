# How to Start the Application

## Step-by-Step Instructions

### 1. Install Backend Dependencies

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE
pip3 install -r requirements.txt
```

**Note:** Some dependencies like PaddleOCR may take time to install. If you encounter issues, you can start the server without PaddleOCR for testing (it will show errors when trying to process documents, but the API will work).

### 2. Configure Environment Variables

Make sure your `.env` file exists and has your API keys:

```bash
# Edit .env file
nano .env
# or
open .env
```

Add your Baidu AI Studio credentials:
```
BAIDU_API_KEY=your_api_key_here
BAIDU_SECRET_KEY=your_secret_key_here
```

### 3. Start Backend Server

**Option A: Using the Python start script (Recommended)**
```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE
python3 start_backend.py
```

**Option B: Using uvicorn directly**
```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE
python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 4. Start Frontend Server (in a new terminal)

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

### 5. Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Troubleshooting

### Backend won't start

1. **Import errors**: Make sure you're running from the project root directory
   ```bash
   cd /Users/PalusS0502/Documents/hackathon/ERNIE
   python3 start_backend.py
   ```

2. **Port already in use**: 
   ```bash
   lsof -i :8000
   # Kill the process if needed
   kill -9 <PID>
   ```

3. **Missing dependencies**:
   ```bash
   pip3 install fastapi uvicorn python-multipart python-dotenv pydantic
   ```

4. **PaddleOCR issues**: The app will work without PaddleOCR, but document processing won't work. You can comment out the OCR initialization temporarily.

### Frontend won't start

1. **Node modules missing**:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   ```

2. **Port 3000 in use**:
   ```bash
   lsof -i :3000
   kill -9 <PID>
   ```

### Test if Backend is Running

```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","timestamp":"..."}
```

## Quick Test

Once both servers are running, test the API:

```bash
# Health check
curl http://localhost:8000/health

# Get API info
curl http://localhost:8000/
```

Then open http://localhost:3000 in your browser to see the frontend.


