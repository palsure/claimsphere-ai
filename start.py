#!/usr/bin/env python3
"""
Startup script for Railway deployment
Reads PORT from environment variable
"""
import os
import sys

# Get PORT from environment, default to 8000
port_str = os.environ.get('PORT', '8000')
try:
    port = int(port_str)
except ValueError:
    print(f"Warning: PORT environment variable '{port_str}' is not a valid integer. Using default 8000.")
    port = 8000

host = os.environ.get('HOST', '0.0.0.0')

print(f"Starting server on {host}:{port}")
print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")

# Import and run uvicorn
import uvicorn
uvicorn.run(
    "backend.app:app",
    host=host,
    port=port,
    log_level="info"
)

