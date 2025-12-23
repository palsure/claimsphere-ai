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

# Copy startup script
COPY start.py /app/start.py
RUN chmod +x /app/start.py

# Expose port (Railway provides PORT env var)
EXPOSE 8000

# Run the application using Python startup script
# This ensures PORT environment variable is properly handled
CMD ["python", "/app/start.py"]

