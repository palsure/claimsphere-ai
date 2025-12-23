FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# Note: libgl1-mesa-glx is deprecated in Debian Trixie, use libgl1 instead
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway provides PORT env var)
EXPOSE ${PORT:-8000}

# Run the application
# Railway uses PORT environment variable
CMD uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}

