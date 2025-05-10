# Megabyzus NASA Agent API

This API service provides a REST interface to interact with the NASA Technology Transfer Agent, allowing the frontend to query NASA patents, software, and spinoff technologies.

## Overview

The Megabyzus NASA Agent API is built with FastAPI and wraps the NASA agent to provide the following features:

- Session management for conversations
- Message interception for future tool call visualization
- RESTful endpoints for conversation interaction
- Error handling and validation
- Health check endpoint

## Setup

### Prerequisites

- Python 3.8+
- Anthropic API key (for Claude model access)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the API directory with the following variables:

```
ANTHROPIC_API_KEY=your_api_key_here
PORT=8000
```

## Available Endpoints

- `POST /api/message` - Process a message with the NASA Agent
- `GET /api/health` - Check API health
- `GET /api/sessions/{session_id}/history` - Get conversation history for a session
- `DELETE /api/sessions/{session_id}` - Delete a session

## Running the API

You can run the API using the provided shell script:

```bash
chmod +x run_api.sh
./run_api.sh
```

Or manually with:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Integration with Frontend

The API is designed to integrate with the Megabyzus frontend. The frontend sends requests to the API and displays the responses in its UI.

### API Response Format

For message processing, the API returns responses in this format:

```json
{
  "response": "The NASA agent's response text",
  "session_id": "unique-session-id-for-continuity"
}
```

## Testing

You can test the API using the built-in OpenAPI documentation at:

```
http://localhost:8000/docs
```

This interactive documentation allows you to try out all the endpoints directly in your browser.

## Development Notes

- The API uses in-memory session storage for simplicity. For production, this should be replaced with a database.
- The message interception middleware is set up to log messages for now, but can be extended to extract and process tool calls.