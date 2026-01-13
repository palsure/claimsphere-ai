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

# Print to both stdout and stderr to ensure visibility in Railway logs
def log_both(message):
    print(message, flush=True)
    print(message, file=sys.stderr, flush=True)

log_both("=" * 60)
log_both("CLAIMSPHERE AI - STARTUP DIAGNOSTICS")
log_both("=" * 60)
log_both(f"Starting server on {host}:{port}")
log_both(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
log_both(f"OLLAMA_BASE_URL: {os.environ.get('OLLAMA_BASE_URL', 'NOT SET')}")
log_both(f"USE_OLLAMA: {os.environ.get('USE_OLLAMA', 'NOT SET')}")
log_both("=" * 60)

# Import and run uvicorn
try:
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
except Exception as e:
    print(f"Error starting server: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

