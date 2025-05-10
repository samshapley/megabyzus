# Megabyzus

Agent of Defence - NASA Technology Data Collection and Analysis

## New Package Structure

The package has been restructured to follow Python best practices:

```
megabyzus/                  # Project root
├── src/                    # Source code directory
│   └── megabyzus/          # Main package
│       ├── __init__.py     # Package initialization
│       ├── agent/          # Agent modules
│       │   ├── nasa_agent.py
│       │   ├── tool_calling_agent.py
│       │   └── ...
│       ├── api/            # API modules
│       │   ├── main.py     # FastAPI application
│       │   └── ...
│       ├── data/           # Data handling modules
│       │   └── nasa/       # NASA data modules
│       │       ├── nasa_api_collector.py
│       │       └── ...
│       └── tools/          # Utility tools
├── setup.py                # Package installation configuration
└── run_api.sh              # Convenience script to run the API
```

## Installation

Install the package in development mode:

```bash
pip install -e .
```

This will make the `megabyzus` package available to import in your Python environment.

## Running the API

You can run the API server using the provided convenience script:

```bash
./run_api.sh
```

This will:
1. Set the necessary environment variables
2. Configure the Python path to find the package
3. Start the FastAPI server on port 8080

## API Endpoints

- `/api/health` - Health check endpoint
- `/api/message` - Send messages to the agent
- `/api/sessions/{session_id}/history` - Get conversation history
- `/api/sessions/{session_id}` - Delete a session

## Environment Variables

- `ANTHROPIC_API_KEY` - API key for the Anthropic Claude service
- `PORT` - Port to run the API server on (default: 8080)

## Dependencies

- FastAPI
- Uvicorn
- Anthropic
- Requests
- Matplotlib
- Tabulate