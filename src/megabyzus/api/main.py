from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from uuid import uuid4
import json

from megabyzus.agent.core_agent import CoreAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nasa-api")

# Initialize the FastAPI app
app = FastAPI(
    title="Megabyzus Agent API",
    description="API for interacting with the Megabyzus agent.",
    version="0.1.0"
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (in a real app, use a proper database)
sessions = {}

# Pydantic models for request/response validation
class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    session_id: str

class Session(BaseModel):
    session_id: str
    created_at: str
    agent: Any

# Middleware for message interception
@app.middleware("http")
async def intercept_messages(request: Request, call_next):
    # Clone the request body
    body = await request.body()
    request_data = None
    
    # Only process specific endpoints
    if request.url.path == "/api/message" and request.method == "POST":
        try:
            request_data = json.loads(body)
            logger.info(f"Intercepted request: {request_data}")
            
            # Here we can modify or log the request if needed
            # For now, just pass it through
        except Exception as e:
            logger.error(f"Error intercepting request: {e}")
    
    # Reconstruct the request with the original body
    request._body = body
    
    # Process the request
    response = await call_next(request)
    
    # Clone the response body
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    # Only process specific endpoints
    if request.url.path == "/api/message" and request.method == "POST":
        try:
            response_data = json.loads(response_body)
            logger.info(f"Intercepted response: {response_data}")
            
            # Here we can modify or log the response if needed
            # For now, just pass it through
        except Exception as e:
            logger.error(f"Error intercepting response: {e}")
    
    # Reconstruct the response with the original body
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

# Helper function to get or create an agent session
def get_or_create_session(session_id: Optional[str] = None) -> Session:
    if session_id and session_id in sessions:
        return sessions[session_id]
    
    # Create a new session with an agent
    new_session_id = session_id or str(uuid4())
    
    # Get API key from environment or use a default for development
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set, using development mode")
    
    # Create a new agent for this session
    core_agent = CoreAgent(api_key=api_key)
    
    # Store the session
    import datetime
    session = Session(
        session_id=new_session_id,
        created_at=datetime.datetime.now().isoformat(),
        agent=core_agent
    )
    sessions[new_session_id] = session
    
    return session

# API Endpoints
@app.post("/api/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    try:
        # Get or create a session
        session = get_or_create_session(request.session_id)
        
        # Process the message with the agent
        response = session.agent.process_message(request.message)
        
        return MessageResponse(
            response=response,
            session_id=session.session_id
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    session = sessions[session_id]
    history = session.agent.get_conversation_history()
    
    return {"session_id": session_id, "history": history}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    del sessions[session_id]
    return {"status": "success", "message": f"Session {session_id} deleted"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
