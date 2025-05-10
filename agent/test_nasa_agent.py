#!/usr/bin/env python3
"""
Test script for the NASA agent.
This script demonstrates how to use the NASA agent to search for NASA technologies,
showing how to set up the agent, send queries, and view the results.
"""
import os
import sys
import json
from typing import Dict, Any

# Add parent directory to path to allow importing from neighboring packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from megabyzus.agent.nasa_agent import NASAAgent

def print_divider(title: str = ""):
    """Print a divider line with optional title."""
    width = 80
    if title:
        print(f"\n{'-' * ((width - len(title) - 4) // 2)} {title} {'-' * ((width - len(title) - 4) // 2)}\n")
    else:
        print(f"\n{'-' * width}\n")

def print_formatted_results(results_json: str, max_items: int = 3):
    """
    Print formatted results from a NASA tool response.
    
    Args:
        results_json: JSON string containing results
        max_items: Maximum number of items to display
    """
    try:
        # Parse the JSON string
        data = json.loads(results_json)
        
        # Check if it's a valid response
        if "status" in data and data["status"] == "success":
            print(f"Query: {data['query']}")
            print(f"Total results found: {data['total_found']}")
            print(f"Results returned: {data['returning']}")
            
            # Display a subset of results
            results = data.get("results", [])
            display_count = min(max_items, len(results))
            
            if display_count > 0:
                print("\nTop results:")
                for i, result in enumerate(results[:display_count]):
                    print(f"\n  Result {i+1}:")
                    print(f"  Title: {result.get('title', 'Unknown')}")
                    print(f"  ID: {result.get('id', 'Unknown')}")
                    print(f"  Case Number: {result.get('case_number', 'Unknown')}")
                    
                    # Truncate description for readability
                    description = result.get('description', 'No description available')
                    if len(description) > 200:
                        description = description[:200] + "..."
                    print(f"  Description: {description}")
                    
                    print(f"  Center: {result.get('center', 'Unknown')}")
                    print(f"  Category: {result.get('category', 'Unknown')}")
            else:
                print("\nNo results to display.")
                
            if len(results) > display_count:
                print(f"\n[...and {len(results) - display_count} more results not shown]")
        else:
            # Handle error responses
            print(f"Error in response: {results_json}")
    
    except json.JSONDecodeError:
        # If it's not valid JSON, just print it as is
        print(results_json)
    except Exception as e:
        print(f"Error parsing results: {e}")
        print(f"Original response: {results_json}")

def main():
    """
    Main function to demonstrate the NASA agent.
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your_api_key_here'")
        return
    
    print_divider("NASA TECHNOLOGY AGENT TEST")
    print("Initializing NASA agent...")
    
    # Initialize the NASA agent
    agent = NASAAgent(api_key=api_key)
    
    # Test a series of queries to demonstrate the agent's capabilities
    test_queries = [
        "I'm looking for NASA patents related to propulsion systems. Can you find some for me?",
        "What software has NASA developed for image processing?",
        "Tell me about NASA spinoff technologies that have applications in healthcare.",
        "Can you search for patents from the JPL center related to robotics?"
    ]
    
    # Process each query and show the response
    for i, query in enumerate(test_queries):
        print_divider(f"TEST QUERY {i+1}")
        print(f"USER: {query}")
        
        # Process the query with verbose output
        print("\nProcessing...\n")
        response = agent.process_message(query, verbose=True)
        
        print(f"\nAGENT RESPONSE: {response}")
    
    print_divider()
    print("Test completed successfully!\n")

if __name__ == "__main__":
    main()