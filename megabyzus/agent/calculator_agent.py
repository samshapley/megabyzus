import os
from typing import Optional
from megabyzus.agent.tool_calling_agent import ToolCallingAgent
from megabyzus.agent.calculator_tools import calculator_tools, process_tool_call

class CalculatorAgent:
    """
    A calculator agent that uses Claude to understand questions and perform calculations.
    This agent uses the ToolCallingAgent for the core interaction logic and provides
    calculator-specific tools.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize the calculator agent with calculator-specific tools.
        
        Args:
            api_key: The Anthropic API key. If None, will use the ANTHROPIC_API_KEY environment variable.
            model: The Claude model to use.
        """
        # Create the base tool-calling agent with calculator tools
        self.agent = ToolCallingAgent(
            tools=calculator_tools,
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
    
    def get_conversation_history(self):
        """Get the entire conversation history."""
        return self.agent.get_conversation_history()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.agent.clear_conversation_history()