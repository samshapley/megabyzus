#!/bin/bash

# Set environment variables (if not already set)
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-"your_default_key_here"}
export PORT=${PORT:-8080}
export PYTHONPATH="$(dirname "$0")/src"

echo "Starting Megabyzus NASA Agent API on port $PORT"
echo "Using ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:3}...${ANTHROPIC_API_KEY: -3}"
echo "PYTHONPATH set to: $PYTHONPATH"

# Start the FastAPI server with the correct module path
cd "$(dirname "$0")"
python -m uvicorn megabyzus.api.main:app --host 0.0.0.0 --port $PORT --reload