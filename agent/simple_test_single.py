#!/usr/bin/env python3
"""
Very simple test script that performs a single calculation.
This is used to diagnose the tool use error.
"""
import os
import sys

# Add parent directory to path to allow importing from neighboring packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from megabyzus.agent.calculator_agent import CalculatorAgent
from megabyzus.agent.calculator_tools import Add

def main():
    """
    Main function to perform a single calculation.
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your_api_key_here'")
        return
    
    print("\n===== Simple Calculator Test =====\n")
    print(f"Tool definition from schema: {Add.tool_definition()}")
    print("\nInitializing calculator agent...")
    
    # Initialize the calculator agent
    agent = CalculatorAgent(api_key=api_key)
    
    # Single test message
    test_message = "What is 25 plus 17?"
    print(f"\nUser: {test_message}")
    
    # Process the message with verbose output
    print("\nProcessing...\n")
    result = agent.process_message(test_message, verbose=True)
    
    print(f"\nFinal Result: {result}")

if __name__ == "__main__":
    main()