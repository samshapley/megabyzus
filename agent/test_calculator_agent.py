#!/usr/bin/env python3
"""
Test script for the calculator agent.
This script demonstrates how to use the calculator agent with conversation memory,
showing how to set up the agent, send messages, and see conversation history.
"""
import os
import json
import sys
from typing import List, Dict, Any

# Add parent directory to path to allow importing from neighboring packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from megabyzus.agent.calculator_agent import CalculatorAgent

def print_divider(title: str = ""):
    """Print a divider line with optional title."""
    width = 80
    if title:
        print(f"\n{'-' * ((width - len(title) - 4) // 2)} {title} {'-' * ((width - len(title) - 4) // 2)}\n")
    else:
        print(f"\n{'-' * width}\n")

def print_conversation_history(messages: List[Dict[str, Any]]):
    """Print the conversation history in a readable format."""
    print_divider("CONVERSATION HISTORY")
    
    for message in messages:
        role = message["role"].upper()
        content = message["content"]
        
        # Handle different content formats
        if isinstance(content, list):
            # For tool results or other structured content
            if len(content) > 0:
                content_item = content[0]
                if isinstance(content_item, dict) and "type" in content_item:
                    content_type = content_item.get("type", "unknown")
                    if content_type == "tool_result":
                        tool_result = content_item.get("content", "")
                        print(f"{role} (TOOL RESULT): {tool_result}")
                    else:
                        print(f"{role} (STRUCTURED): {json.dumps(content, indent=2)}")
                else:
                    print(f"{role} (STRUCTURED): {content}")
            else:
                print(f"{role}: [Empty content list]")
        elif isinstance(content, str):
            # For simple string content
            print(f"{role}: {content}")
        else:
            # For Claude's content blocks
            if hasattr(content, "__iter__"):
                # Try to extract text from content blocks
                text_blocks = []
                for block in content:
                    if hasattr(block, "text") and block.text:
                        text_blocks.append(block.text)
                    elif hasattr(block, "type") and block.type == "tool_use":
                        text_blocks.append(f"[TOOL USE: {block.name}] with input: {block.input}")
                
                if text_blocks:
                    print(f"{role}: {' '.join(text_blocks)}")
                else:
                    print(f"{role}: [Complex content structure]")
            else:
                print(f"{role}: {content}")
    
    print_divider()

def main():
    """
    Main function to demonstrate the calculator agent.
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your_api_key_here'")
        return
    
    print_divider("CALCULATOR AGENT TEST")
    print("Initializing calculator agent...")
    
    # Initialize the calculator agent
    agent = CalculatorAgent(api_key=api_key)
    
    # Test series of calculations with conversation memory
    test_messages = [
        "What is 42 plus 18?",
        "Multiply that result by 2.5",
        "If I divide the previous result by 15, what do I get?",
        "Can you subtract 10 from that and then multiply by 3?"
    ]
    
    # Process each message and show the response
    for i, message in enumerate(test_messages):
        print_divider(f"TEST MESSAGE {i+1}")
        print(f"USER: {message}")
        
        # Process the message
        response = agent.process_message(message, verbose=True)
        
        print(f"\nAGENT: {response}")
    
    # Show the full conversation history
    print_conversation_history(agent.get_conversation_history())
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()