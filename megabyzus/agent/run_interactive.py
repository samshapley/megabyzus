#!/usr/bin/env python3
"""
Interactive script for the calculator agent.
This script allows you to have a conversation with the calculator agent
using the refactored implementation with Pydantic model-based tool definitions.
"""
import os
import sys

# Add parent directory to path to allow importing from neighboring packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from megabyzus.agent.calculator_agent import CalculatorAgent
from megabyzus.agent.calculator_tools import Add, Subtract, Multiply, Divide

def main():
    """
    Main function to run an interactive session with the calculator agent.
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your_api_key_here'")
        return
    
    print("\n===== Calculator Agent Interactive Session =====\n")
    print("This script allows you to interact with the calculator agent.")
    print("The agent can perform basic math operations and maintains conversation memory.")
    print("Available tools:")
    
    # Display available tools
    for tool_class in [Add, Subtract, Multiply, Divide]:
        print(f"- {tool_class.__name__}: {tool_class.__doc__}")
    
    print("\nType 'exit', 'quit', or 'q' to end the conversation.")
    
    # Initialize the calculator agent
    agent = CalculatorAgent(api_key=api_key)
    
    print("\nCalculator agent initialized. Start typing your math questions!\n")
    
    # Interactive loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nEnding conversation. Goodbye!")
            break
        
        # Process the user input
        print("\nProcessing...")
        response = agent.process_message(user_input)
        
        # Display the response
        print(f"\nAgent: {response}")

if __name__ == "__main__":
    main()