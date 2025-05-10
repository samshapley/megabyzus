import os
import re
from typing import List, Dict, Any, Optional, Callable
from anthropic import Anthropic
from pydantic import BaseModel
import json

# Helper function to convert CamelCase to snake_case
def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

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
        self.messages = []
    
    def _format_response(self, response: Any) -> str:
        """Format the final response from Claude."""
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )
        return final_response
    
    def process_message(self, user_message: str, verbose: bool = False) -> str:
        """
        Process a user message, maintain conversation memory, and return the response.
        
        Args:
            user_message: The message from the user.
            verbose: Whether to print detailed information about the interaction.
            
        Returns:
            The agent's response.
        """
        if verbose:
            print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
        
        # Add user message to the conversation memory
        self.messages.append({"role": "user", "content": user_message})

        # save self.messages to a file json
        with open("conversation_history.json", "w") as f:
            json.dump(self.messages, f, indent=2)
        
        # Initial message to Claude with the conversation history
        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            tools=self.tools,
            system=self.system,
            messages=self.messages,
        )
        
        if verbose:
            print(f"\nInitial Response:")
            print(f"Stop Reason: {message.stop_reason}")
            print(f"Content: {message.content}")
        
        # Add Claude's response to conversation memory
        self.messages.append({"role": "assistant", "content": message.content})
        
        # If Claude wants to use a tool
        if message.stop_reason == "tool_use":
            tool_use = next(block for block in message.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            if verbose:
                print(f"\nTool Used: {tool_name}")
                print(f"Tool Input: {tool_input}")
            
            # Process the tool call using the provided function
            tool_result = self.process_tool_call_func(tool_name, tool_input)
            
            if verbose:
                print(f"Tool Result: {tool_result}")
            
            # Add tool result to conversation memory
            self.messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": tool_result,
                    }
                ],
            })
            
            # Get the final response from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=self.messages,
                tools=self.tools,
            )
            
            # Add final response to conversation memory
            self.messages.append({"role": "assistant", "content": response.content})
            
            final_response = self._format_response(response)
        else:
            final_response = self._format_response(message)
        
        if verbose:
            print(f"\nFinal Response: {final_response}")
        
        return final_response
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the entire conversation history."""
        return self.messages
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.messages = []