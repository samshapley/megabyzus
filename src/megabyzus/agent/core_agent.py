import os
from typing import Optional, List, Dict, Any, Union

# Import base agent class
from megabyzus.agent.tool_calling_agent import ToolCallingAgent
# Import NASA tools
from megabyzus.agent.nasa_tools import nasa_tools, process_tool_call

class CoreAgent:

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet-20250219"):
        """
        Args:
            api_key: The Anthropic API key. If None, will use the ANTHROPIC_API_KEY environment variable.
            model: The Claude model to use.
        """
        system = (
            "You are Megabyzus, named after the ancient Persian general."
            "Use tools and return helpful information to the user."
        )

        self.agent = ToolCallingAgent(
            tools=nasa_tools,
            system=system,
            process_tool_call_func=process_tool_call,
            api_key=api_key,
            model=model
        )
    
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
        # Add the user message to conversation memory in the agent
        user_message_dict = {"role": "user", "content": user_message}
        
        # Get the initial response from Claude using the existing agent
        # But we'll handle the message ourselves to avoid modifying the agent's state
        from anthropic import Anthropic
        client = self.agent.client
        
        # Get all messages for context, including the user's new message
        messages_for_api_call = self.agent.messages_api.copy() + [user_message_dict]
        
        message = client.messages.create(
            model=self.agent.model,
            max_tokens=8000,
            tools=self.agent.tools,
            system=self.agent.system,
            messages=messages_for_api_call,
        )
        
        if verbose:
            print(f"\nInitial Response:")
            print(f"Stop Reason: {message.stop_reason}")
            print(f"Content: {message.content}")
        
        # Extract text from the response
        final_response = next(
            (block.text for block in message.content if hasattr(block, "text")),
            None,
        )
        
        # Identify if there are pending tool calls
        has_tool_calls = message.stop_reason == "tool_use"
        tool_uses = [block for block in message.content if block.type == "tool_use"] if has_tool_calls else []
        
        # Extract information about pending tool calls without processing them
        import time
        pending_tool_calls = []
        for tool_use in tool_uses:
            pending_tool_calls.append({
                "id": tool_use.id,
                "toolName": tool_use.name,
                "inputs": tool_use.input,
                "timestamp": int(time.time() * 1000)  # Current time in milliseconds
            })
        
        # Add the message to the agent's conversation history
        # Only if there are no tool calls (otherwise, let the process_message handle it)
        if not has_tool_calls:
            self.agent.messages_api.append(user_message_dict)
            self.agent.messages.append(user_message_dict)
            
            self.agent.messages_api.append({"role": "assistant", "content": message.content})
            self.agent.messages.append({"role": "assistant", "content": self.agent._format_response(message)})
        
        return {
            "response": final_response,
            "pending_tool_calls": pending_tool_calls,
            "has_pending_tool_calls": has_tool_calls
        }
    
    def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Process a single tool call and return the result.
        
        Args:
            tool_name: The name of the tool to call.
            tool_input: The input parameters for the tool.
            
        Returns:
            The result of the tool call as a string.
        """
        return process_tool_call(tool_name, tool_input)
    
    def process_message(self, user_message: str, verbose: bool = False) -> dict:
        """
        Process a user message, maintain conversation memory, and return the response.
        Delegates to the base tool-calling agent.
        
        Args:
            user_message: The message from the user.
            verbose: Whether to print detailed information about the interaction.
            
        Returns:
            A dictionary containing the response text and tool calls if any.
        """
        # Process the message and get both the response and tool calls
        result = self.agent.process_message(user_message, verbose)
        
        # If the result is already a dict with response and tool_calls, return it directly
        if isinstance(result, dict) and 'response' in result:
            return result
            
        # Otherwise (for backward compatibility), convert the string response to the new format
        return {
            "response": result,
            "tool_calls": self.agent.get_latest_tool_calls()
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the entire conversation history."""
        return self.agent.get_conversation_history()
    
    def get_latest_tool_calls(self) -> List[Dict[str, Any]]:
        """Get the tool calls from the latest message."""
        return self.agent.get_latest_tool_calls()
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.agent.clear_conversation_history()