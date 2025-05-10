import os
from typing import Optional, List, Dict, Any

# Import base agent class
from megabyzus.agent.tool_calling_agent import ToolCallingAgent
# Import NASA tools
from megabyzus.agent.nasa_tools import nasa_tools, process_tool_call

class CoreAgent:

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
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
    
    def process_message(self, user_message: str, verbose: bool = False) -> str:
        """
        Process a user message, maintain conversation memory, and return the response.
        Delegates to the base tool-calling agent.
        
        Args:
            user_message: The message from the user.
            verbose: Whether to print detailed information about the interaction.
            
        Returns:
            The agent's response.
        """
        return self.agent.process_message(user_message, verbose)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the entire conversation history."""
        return self.agent.get_conversation_history()
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.agent.clear_conversation_history()