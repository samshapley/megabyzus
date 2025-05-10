#!/bin/bash

# Run script for the calculator agent
# This script makes it easy to run the calculator agent

# Set the API key if provided as an argument
if [ $# -eq 1 ]; then
  export ANTHROPIC_API_KEY="$1"
  echo "API key set from command line argument"
elif [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set"
  echo "Please provide it as an argument to this script:"
  echo "  ./run.sh sk-ant-api03-your-key-here"
  echo "Or set it in your environment:"
  echo "  export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'"
  exit 1
fi

# Install required packages if needed
echo "Checking for required packages..."
pip list | grep -q "anthropic" || {
  echo "Installing anthropic package..."
  pip install anthropic pydantic 'pydantic[email]'
}

# Run the interactive test
echo "Starting calculator agent..."
python simple_test.py