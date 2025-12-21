# Start the Application Locally

## Quick Start (Using Scripts)

### Terminal 1 - Backend (with venv)

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE
./start_backend_venv.sh
```

This will:
- Create/activate virtual environment
- Install dependencies
- Start the backend server on http://localhost:8000

### Terminal 2 - Frontend

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE
./start_frontend.sh
```

This will:
- Install npm dependencies (if needed)
- Start the frontend server on http://localhost:3000

## Manual Start

### Backend with Virtual Environment

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start server
python3 start_backend.py
```

### Frontend

```bash
cd /Users/PalusS0502/Documents/hackathon/ERNIE/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Access the Application

Once both servers are running:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Environment Variables

Make sure your `.env` file exists and has your API keys:

```bash
# Copy template if needed
cp env.template .env

# Edit .env file
nano .env
```

Add your Baidu AI Studio credentials:
```
BAIDU_API_KEY=your_api_key_here
BAIDU_SECRET_KEY=your_secret_key_here
```

## Troubleshooting

### Backend Issues

1. **Virtual environment not activating**:
   ```bash
   source venv/bin/activate
   which python  # Should show venv path
   ```

2. **Dependencies not installing**:
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Port 8000 already in use**:
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

4. **Import errors**: Make sure you're in the project root and venv is activated

### Frontend Issues

1. **Node modules missing**:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port 3000 in use**:
   ```bash
   lsof -i :3000
   kill -9 <PID>
   ```

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"..."}
```

## Stopping the Servers

Press `Ctrl+C` in each terminal, or:

```bash
# Find and kill processes
pkill -f "uvicorn"
pkill -f "next dev"
```

## Notes

- The backend uses a virtual environment to isolate dependencies
- The frontend uses npm/node_modules
- Both servers support hot-reload (auto-restart on code changes)
- Backend API docs are available at http://localhost:8000/docs

