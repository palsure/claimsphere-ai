FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# Note: libgl1-mesa-glx is deprecated in Debian Trixie, use libgl1 instead
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    postgresql-client \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install psutil first (it's a common dependency that needs compilation)
# This helps with build caching and error isolation
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir psutil && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Copy startup script
COPY start.py /app/start.py
RUN chmod +x /app/start.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application using Python startup script
# This ensures PORT environment variable is properly handled
CMD ["python", "/app/start.py"]

