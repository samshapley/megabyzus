from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from uuid import uuid4
import json
import asyncio
import threading

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

# In-memory tool call storage (in a real app, use a proper database)
tool_call_store = {}

# Background processing lock to prevent race conditions
processing_lock = threading.Lock()

# Pydantic models for request/response validation
class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ToolCallStatus(BaseModel):
    tool_call_id: str
    status: str  # "pending" or "completed"
    result: Optional[Any] = None

class ToolCallStatusRequest(BaseModel):
    session_id: str
    tool_call_ids: List[str]

class ToolCallStatusResponse(BaseModel):
    tool_calls: List[ToolCallStatus]

class MessageResponse(BaseModel):
    response: str
    session_id: str
    toolCalls: Optional[List[Dict[str, Any]]] = None

class Session(BaseModel):
    session_id: str
    created_at: str
    agent: Any

# Function to process tool calls in the background
def process_tool_call(session_id, tool_id, tool_name, inputs, timestamp):
    """Process a single tool call and update the tool call store with results."""
    try:
        # Get the session
        session = sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found when processing tool call")
            return
        
        # Process the tool call
        result = session.agent.process_tool_call(tool_name, inputs)
        
        # Update the tool call store with the result
        with processing_lock:
            if session_id in tool_call_store and tool_id in tool_call_store[session_id]:
                tool_call_store[session_id][tool_id].update({
                    "status": "completed",
                    "result": result
                })
                
        logger.info(f"Tool call {tool_id} processed successfully")
    except Exception as e:
        logger.error(f"Error processing tool call {tool_id}: {str(e)}")
        # Update the tool call store with the error
        with processing_lock:
            if session_id in tool_call_store and tool_id in tool_call_store[session_id]:
                tool_call_store[session_id][tool_id].update({
                    "status": "error",
                    "result": f"Error: {str(e)}"
                })

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
    
    # Initialize tool call store for this session
    tool_call_store[new_session_id] = {}
    
    return session

# API Endpoints
@app.post("/api/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    try:
        # Get or create a session
        session = get_or_create_session(request.session_id)
        
        # Process the initial message with the agent
        result = session.agent.get_initial_response(request.message)
        
        # Extract response text and pending tool calls from the result
        if isinstance(result, dict) and 'response' in result and 'pending_tool_calls' in result:
            response_text = result['response']
            pending_tool_calls = result['pending_tool_calls']
            
            # Store pending tool calls in the tool call store
            for tool_call in pending_tool_calls:
                tool_id = tool_call['id']
                # Store with a pending status
                tool_call_store[session.session_id][tool_id] = {
                    "status": "pending",
                    "toolName": tool_call["toolName"],
                    "inputs": tool_call["inputs"],
                    "id": tool_id,
                    "timestamp": tool_call["timestamp"]
                }
            
            # Process tool calls in the background
            for tool_call in pending_tool_calls:
                # Start a new thread for each tool call
                tool_thread = threading.Thread(
                    target=process_tool_call,
                    args=(
                        session.session_id,
                        tool_call['id'],
                        tool_call['toolName'],
                        tool_call['inputs'],
                        tool_call['timestamp']
                    )
                )
                tool_thread.daemon = True  # Set as daemon so it won't block shutdown
                tool_thread.start()
            
            # Return the response with pending tool calls
            return MessageResponse(
                response=response_text,
                session_id=session.session_id,
                toolCalls=pending_tool_calls
            )
        else:
            # For backward compatibility
            response_text = result
            tool_calls = session.agent.get_latest_tool_calls() if hasattr(session.agent, 'get_latest_tool_calls') else None
            
            return MessageResponse(
                response=response_text,
                session_id=session.session_id,
                toolCalls=tool_calls
            )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/api/tool-call-status", response_model=ToolCallStatusResponse)
async def check_tool_call_status(request: ToolCallStatusRequest):
    """Check the status of tool calls for a session."""
    try:
        # Verify the session exists
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
        
        # Verify the tool call store exists for this session
        if request.session_id not in tool_call_store:
            raise HTTPException(status_code=404, detail=f"No tool calls found for session {request.session_id}")
        
        # Get the status of each tool call
        tool_calls = []
        
        with processing_lock:
            for tool_id in request.tool_call_ids:
                if tool_id in tool_call_store[request.session_id]:
                    tool_call_info = tool_call_store[request.session_id][tool_id]
                    tool_calls.append({
                        "tool_call_id": tool_id,
                        "status": tool_call_info["status"],
                        "result": tool_call_info.get("result"),
                        "toolName": tool_call_info["toolName"],
                        "inputs": tool_call_info["inputs"],
                        "timestamp": tool_call_info["timestamp"]
                    })
                else:
                    tool_calls.append({
                        "tool_call_id": tool_id,
                        "status": "not_found"
                    })
        
        return ToolCallStatusResponse(tool_calls=tool_calls)
    except Exception as e:
        logger.error(f"Error checking tool call status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking tool call status: {str(e)}")

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
    
    # Clean up tool call store for this session
    if session_id in tool_call_store:
        del tool_call_store[session_id]
    
    del sessions[session_id]
    return {"status": "success", "message": f"Session {session_id} deleted"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)