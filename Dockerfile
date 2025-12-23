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

# Copy and make startup script executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port (Railway provides PORT env var)
EXPOSE 8000

# Run the application using startup script
# This ensures PORT environment variable is properly handled
CMD ["/app/start.sh"]

