import os
import re
import time
from typing import List, Dict, Any, Optional, Callable, Union
from anthropic import Anthropic
from pydantic import BaseModel
import json

# Helper function to convert CamelCase to snake_case
def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

# Helper function to convert Claude API content to JSON serializable format
def content_to_serializable(content):
    """
    Convert Claude API content to a JSON serializable format.
    
    Args:
        content: Content from Claude API which might contain TextBlock objects
        
    Returns:
        JSON serializable representation of the content
    """
    if hasattr(content, '__iter__') and not isinstance(content, (str, dict)):
        # If content is an iterable (like a list)
        return [content_to_serializable(item) for item in content]
    elif hasattr(content, 'type') and hasattr(content, 'text'):
        # If it's a TextBlock
        return {"type": content.type, "text": content.text}
    elif hasattr(content, 'type') and hasattr(content, 'input') and hasattr(content, 'id'):
        # If it's a ToolUseBlock
        return {
            "type": content.type, 
            "id": content.id,
            "name": content.name if hasattr(content, 'name') else None,
            "input": content.input
        }
    elif isinstance(content, dict):
        # Process dictionaries recursively
        return {k: content_to_serializable(v) for k, v in content.items()}
    else:
        # Return other types as is
        return content

# Base class for all tools - moved from calculator_tools.py
class Tool(BaseModel):
    """Base class for all tool schemas."""
    
    @classmethod
    def tool_name(cls):
        """Get the tool name by converting the class name to snake_case."""
        return camel_to_snake(cls.__name__)
    
    @classmethod
    def tool_description(cls):
        """Get the tool description from the class docstring."""
        return cls.__doc__.strip() if cls.__doc__ else ""
    
    @classmethod
    def tool_definition(cls):
        """Generate the tool definition for the Anthropic API."""
        return {
            "name": cls.tool_name(),
            "description": cls.tool_description(),
            "input_schema": cls.model_json_schema()
        }

class ToolCallingAgent:
    """
    A generic tool-calling agent that interfaces with Anthropic's Claude.
    
    This agent provides the core functionality to:
    1. Maintain conversation memory
    2. Send messages to Claude with tools
    3. Process tool calls and return results
    4. Format responses for the user
    
    Any domain-specific agent can extend or compose with this class
    to create specialized tool-calling agents.
    """

    def __init__(
        self, 
        tools: List[Dict[str, Any]],
        process_tool_call_func: Callable[[str, Dict[str, Any]], str],
        system: str = "You are a helpful assistant.",
        api_key: Optional[str] = None, 
        model: str = "claude-3-7-sonnet-20250219"
    ):
        """
        Initialize the tool-calling agent.
        
        Args:
            tools: List of tools available to the agent in Anthropic API format
            process_tool_call_func: Function to process tool calls and return results
            api_key: The Anthropic API key. If None, will use the ANTHROPIC_API_KEY environment variable.
            model: The Claude model to use.
        """
        # Use provided API key or get from environment
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError("No API key provided and ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.tools = tools
        self.process_tool_call_func = process_tool_call_func
        self.system = system
        
        # Initialize conversation memory
        # We will maintain two versions of the messages:
        # 1. messages_api - for sending to the Claude API (with original content objects)
        # 2. messages - for storing and potentially serializing (with serialized content)
        self.messages_api = []  # For API calls
        self.messages = []      # For storage and serialization
        
        # Track the latest tool calls
        self.latest_tool_calls = []
    
    def _format_response(self, response: Any) -> str:
        """Format the final response from Claude."""
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )
        return final_response
        
    def _extract_pending_tool_calls(self, message, verbose=False):
        """
        Extract pending tool calls from a Claude message without processing them.
        
        Args:
            message: The message from Claude that contains tool_use blocks
            verbose: Whether to print detailed information
            
        Returns:
            tuple: (list of pending tool calls, final_response)
        """
        # Extract all tool_use blocks
        tool_uses = [block for block in message.content if block.type == "tool_use"]
        
        pending_tool_calls = []
        
        # Process each tool call
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            if verbose:
                print(f"\nTool Identified: {tool_name}")
                print(f"Tool Input: {tool_input}")
            
            # Create a pending tool call entry (without executing it)
            tool_call_data = {
                "id": tool_use.id,
                "toolName": tool_name,
                "inputs": tool_input,
                "output": None,  # Output is None because it's pending
                "timestamp": int(time.time() * 1000)  # Current time in milliseconds
            }
            pending_tool_calls.append(tool_call_data)
        
        # Extract text response
        final_response = self._format_response(message)
        
        return pending_tool_calls, final_response
        
    def _process_all_tool_calls(self, message, verbose=False):
        """
        Process all tool calls in a message and update the conversation memory.
        
        Args:
            message: The message from Claude that contains tool_use blocks
            verbose: Whether to print detailed information
            
        Returns:
            List of processed tool calls with their results
        """
        # Extract all tool_use blocks
        tool_uses = [block for block in message.content if block.type == "tool_use"]
        
        tool_results = []
        tool_call_contents = []
        
        # Process each tool call
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            if verbose:
                print(f"\nTool Used: {tool_name}")
                print(f"Tool Input: {tool_input}")
            
            # Process the tool call using the provided function
            tool_result = self.process_tool_call_func(tool_name, tool_input)
            
            # Record the tool call for later inclusion in the response
            tool_call_data = {
                "id": tool_use.id,
                "toolName": tool_name,
                "inputs": tool_input,
                "output": tool_result,
                "timestamp": int(time.time() * 1000)  # Current time in milliseconds
            }
            self.latest_tool_calls.append(tool_call_data)
            tool_results.append(tool_call_data)
            
            # Add this tool result to the list of tool results
            tool_call_content = {
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_result,
            }
            tool_call_contents.append(tool_call_content)
            
            if verbose:
                print(f"Tool Result: {tool_result}")
        
        # Create a message with the tool results
        tool_results_message = {
            "role": "user",
            "content": tool_call_contents,
        }
        
        # Add tool results to both API messages and storage messages
        self.messages_api.append(tool_results_message)
        self.messages.append(tool_results_message)  # This is already serializable
        
        return tool_results
    
    def get_initial_response(self, user_message: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Get the initial response from the agent, which may include pending tool calls.
        Does not process the tool calls, just identifies the need for them.
        
        Args:
            user_message: The message from the user.
            verbose: Whether to print detailed information about the interaction.
            
        Returns:
            A dictionary containing the initial response text and pending tool calls if any.
        """
        if verbose:
            print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
        
        # Reset tool calls for new message
        self.latest_tool_calls = []
        
        # Add user message to both conversation memory variants
        user_message_dict = {"role": "user", "content": user_message}
        self.messages_api.append(user_message_dict)
        self.messages.append(user_message_dict)
        
        # Initial message to Claude with the API-formatted conversation history
        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            tools=self.tools,
            system=self.system,
            messages=self.messages_api,
        )
        
        if verbose:
            print(f"\nInitial Response:")
            print(f"Stop Reason: {message.stop_reason}")
            print(f"Content: {message.content}")
        
        # Add Claude's response to conversation memory
        # For API messages, keep the original content
        self.messages_api.append({"role": "assistant", "content": message.content})
        # For storage messages, convert to serializable format
        self.messages.append({"role": "assistant", "content": content_to_serializable(message.content)})
        
        # If Claude wants to use a tool, extract pending tool calls
        if message.stop_reason == "tool_use":
            pending_tool_calls, response_text = self._extract_pending_tool_calls(message, verbose)
            
            return {
                "response": response_text,
                "pending_tool_calls": pending_tool_calls
            }
        else:
            # If no tool calls, just return the response text
            final_response = self._format_response(message)
            return {
                "response": final_response,
                "pending_tool_calls": []
            }
    
    def process_message(self, user_message: str, verbose: bool = False) -> dict:
        """
        Process a user message, maintain conversation memory, and return the response.
        
        Args:
            user_message: The message from the user.
            verbose: Whether to print detailed information about the interaction.
            
        Returns:
            A dictionary containing the agent's response text and tool calls if any.
        """
        if verbose:
            print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
        
        # Reset tool calls for new message
        self.latest_tool_calls = []
        
        # Add user message to both conversation memory variants
        user_message_dict = {"role": "user", "content": user_message}
        self.messages_api.append(user_message_dict)
        self.messages.append(user_message_dict)
        
        # Initial message to Claude with the API-formatted conversation history
        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            tools=self.tools,
            system=self.system,
            messages=self.messages_api,
        )
        
        if verbose:
            print(f"\nInitial Response:")
            print(f"Stop Reason: {message.stop_reason}")
            print(f"Content: {message.content}")
        
        # Add Claude's response to conversation memory
        # For API messages, keep the original content
        self.messages_api.append({"role": "assistant", "content": message.content})
        # For storage messages, convert to serializable format
        self.messages.append({"role": "assistant", "content": content_to_serializable(message.content)})
        
        # If Claude wants to use a tool
        if message.stop_reason == "tool_use":
            # Process all tool calls in the message
            self._process_all_tool_calls(message, verbose)
            
            # Get the final response from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=self.messages_api,  # Use API-formatted messages
                tools=self.tools,
            )
            
            # Check if there are more tool calls in the response
            if response.stop_reason == "tool_use":
                # Process these tool calls too
                self._process_all_tool_calls(response, verbose)
                
                # Get one more response from Claude
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=self.messages_api,  # Use API-formatted messages
                    tools=self.tools,
                )
            
            # Add final response to conversation memory
            # For API messages, keep the original content
            self.messages_api.append({"role": "assistant", "content": response.content})
            # For storage messages, convert to serializable format
            self.messages.append({"role": "assistant", "content": content_to_serializable(response.content)})
            
            final_response = self._format_response(response)
        else:
            final_response = self._format_response(message)
        
        if verbose:
            print(f"\nFinal Response: {final_response}")
        
        # Return both the text response and tool calls
        return {
            "response": final_response,
            "tool_calls": self.latest_tool_calls
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the entire conversation history in serializable format."""
        return self.messages
    
    def get_latest_tool_calls(self) -> List[Dict[str, Any]]:
        """Get the tool calls from the latest message."""
        return self.latest_tool_calls
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.messages_api = []
        self.messages = []
        self.latest_tool_calls = []