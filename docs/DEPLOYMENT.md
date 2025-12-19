# Deployment Guide

## Local Development

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Baidu AI Studio API credentials
```

3. Run the backend server:
```bash
python backend/app.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Production Deployment

### Backend Deployment

#### Option 1: Deploy to Cloud (Heroku, Railway, etc.)

1. Create a `Procfile`:
```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

2. Set environment variables in your hosting platform:
- `BAIDU_API_KEY`
- `BAIDU_SECRET_KEY`
- `FRONTEND_URL`

3. Deploy using your platform's instructions.

#### Option 2: Docker Deployment

1. Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t expense-intelligence .
docker run -p 8000:8000 -e BAIDU_API_KEY=your_key -e BAIDU_SECRET_KEY=your_secret expense-intelligence
```

### Frontend Deployment

#### Deploy to Vercel (Recommended)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

#### Deploy to Netlify

1. Build the project:
```bash
cd frontend
npm run build
```

2. Deploy the `out` directory to Netlify.

## GitHub Pages Deployment (Warm-up Task)

1. Build the warm-up page:
```bash
# The warmup/index.html is already ready
```

2. Enable GitHub Pages in your repository settings.

3. Set the source to the `warmup` directory.

4. Update the API URL in `warmup/index.html` to point to your deployed backend.

## Environment Variables

Required environment variables:

- `BAIDU_API_KEY`: Your Baidu AI Studio API key
- `BAIDU_SECRET_KEY`: Your Baidu AI Studio secret key
- `FRONTEND_URL`: Frontend URL for CORS (production)
- `PORT`: Backend port (default: 8000)
- `DEBUG`: Debug mode (default: True)

## CORS Configuration

Update CORS settings in `backend/app.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

