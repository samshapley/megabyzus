#!/usr/bin/env python3
"""
Mock test script for the NASA agent.
This script demonstrates the NASA agent functionality using mocked API responses,
allowing for testing without actual API calls or API keys.
"""
import os
import sys
import json
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

# Add parent directory to path to allow importing from neighboring packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# First patch NASA API modules to prevent any real API calls
patent_api_patch = patch('megabyzus.data.nasa.nasa_patent_api')
software_api_patch = patch('megabyzus.data.nasa.nasa_software_api')
spinoff_api_patch = patch('megabyzus.data.nasa.nasa_spinoff_api')
anthropic_patch = patch('anthropic.Anthropic')

# Start patches
mock_patent_api = patent_api_patch.start()
mock_software_api = software_api_patch.start()
mock_spinoff_api = spinoff_api_patch.start()
mock_anthropic = anthropic_patch.start()

# Import after patching to ensure no real API calls
from megabyzus.agent.nasa_agent import NASAAgent
from megabyzus.agent.nasa_tools import process_tool_call

class MockContent:
    """Mock content class for Anthropic API responses."""
    def __init__(self, type_value, **kwargs):
        self.type = type_value
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_tool_use_response(tool_name, tool_input, message_text):
    """Create a mock tool use response."""
    content = [
        MockContent("tool_use", name=tool_name, id=f"tool_{tool_name}_123", input=tool_input),
        MockContent("text", text=message_text)
    ]
    return MagicMock(stop_reason="tool_use", content=content)

def create_text_response(text):
    """Create a mock text response."""
    content = [MockContent("text", text=text)]
    return MagicMock(stop_reason="end_turn", content=content)

def setup_mock_nasa_apis():
    """Set up mock NASA API responses."""
    # Mock search_patents function
    mock_patent_api.search_patents.return_value = {
        "results": [
            [
                "U-12345", 
                "LEW-CASE-12345", 
                "Advanced Propulsion System", 
                "A revolutionary propulsion system that uses quantum mechanics...",
                "John Doe",
                "Propulsion",
                "https://technology.nasa.gov/patent/LEW-CASE-12345",
                "Available",
                "2023-03-15",
                "Glenn Research Center (GRC)"
            ],
            [
                "U-23456", 
                "JSC-CASE-23456", 
                "Improved Rocket Engine", 
                "A more efficient rocket engine design that reduces fuel consumption...",
                "Jane Smith",
                "Propulsion",
                "https://technology.nasa.gov/patent/JSC-CASE-23456",
                "Available",
                "2022-07-22",
                "Johnson Space Center (JSC)"
            ]
        ],
        "count": 2,
        "total": 2,
        "api_type": "patent"
    }
    
    # Mock search_software function
    mock_software_api.search_software.return_value = {
        "results": [
            [
                "S-54321", 
                "GSC-SW-54321", 
                "NASA Image Processing Toolkit", 
                "A comprehensive toolkit for processing and analyzing scientific imagery...",
                "Maria Rodriguez",
                "Image Processing",
                "https://technology.nasa.gov/software/GSC-SW-54321",
                "Open Source",
                "2021-11-30",
                "Goddard Space Flight Center (GSFC)"
            ],
            [
                "S-65432", 
                "ARC-SW-65432", 
                "Advanced Visualization Suite", 
                "Software for 3D visualization of complex scientific data sets...",
                "Robert Johnson",
                "Data Visualization",
                "https://technology.nasa.gov/software/ARC-SW-65432",
                "Government Purpose",
                "2022-05-18",
                "Ames Research Center (ARC)"
            ]
        ],
        "count": 2,
        "total": 2,
        "api_type": "software"
    }
    
    # Mock search_spinoffs function
    mock_spinoff_api.search_spinoffs.return_value = {
        "results": [
            [
                "SP-10101", 
                "JPL-SO-10101", 
                "Medical Imaging Technology", 
                "Medical imaging technology derived from space telescope optics...",
                "Lisa Chen",
                "Healthcare",
                "https://technology.nasa.gov/spinoff/JPL-SO-10101",
                "Commercial",
                "2020-04-12",
                "Jet Propulsion Laboratory (JPL)"
            ],
            [
                "SP-20202", 
                "JSC-SO-20202", 
                "Heart Pump Technology", 
                "Miniature heart pump based on NASA fuel pump designs...",
                "Michael Brown",
                "Healthcare",
                "https://technology.nasa.gov/spinoff/JSC-SO-20202",
                "Commercial",
                "2019-08-23",
                "Johnson Space Center (JSC)"
            ]
        ],
        "count": 2,
        "total": 2,
        "api_type": "spinoff"
    }

def setup_mock_anthropic():
    """Set up mock Anthropic API responses."""
    # Set up the mock client
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    
    # Set up the messages.create method
    mock_messages = MagicMock()
    mock_client.messages = mock_messages
    
    # Set up mock responses for different queries
    mock_responses = [
        # First query: propulsion patents
        create_tool_use_response(
            "search_patents", 
            {"query": "propulsion"}, 
            "I'll search for NASA patents related to propulsion systems."
        ),
        create_text_response("I found 2 NASA patents related to propulsion systems. The first is an 'Advanced Propulsion System' from Glenn Research Center, which uses quantum mechanics. The second is an 'Improved Rocket Engine' from Johnson Space Center, which increases efficiency and reduces fuel consumption. Both patents are available for licensing."),
        
        # Second query: image processing software
        create_tool_use_response(
            "search_software", 
            {"query": "image processing"}, 
            "I'll look for NASA software related to image processing."
        ),
        create_text_response("NASA has developed several software packages for image processing. The NASA Image Processing Toolkit from Goddard Space Flight Center provides comprehensive tools for processing and analyzing scientific imagery. There's also an Advanced Visualization Suite from Ames Research Center for 3D visualization of complex data sets. The Image Processing Toolkit is available as open source while the Visualization Suite is available for government purposes."),
        
        # Third query: healthcare spinoffs
        create_tool_use_response(
            "search_spinoffs", 
            {"query": "healthcare"}, 
            "I'll search for NASA spinoff technologies with healthcare applications."
        ),
        create_text_response("NASA's technology has led to several important healthcare innovations. For example, medical imaging technology derived from space telescope optics was developed at the Jet Propulsion Laboratory. Johnson Space Center contributed to miniature heart pump technology based on NASA fuel pump designs. Both of these spinoff technologies have been commercialized and are improving healthcare outcomes today."),
        
        # Fourth query: JPL robotics patents
        create_tool_use_response(
            "search_patents", 
            {"query": "robotics", "center": "JPL"}, 
            "I'll search for JPL patents related to robotics."
        ),
        create_text_response("I searched for robotics patents from JPL, but the API returned no results matching those criteria. You might want to try broadening your search to include all NASA centers or different keywords related to robotics such as 'autonomous systems' or 'rover technology'.")
    ]
    
    # Configure the mock to return the responses
    mock_messages.create.side_effect = mock_responses
    
    return mock_client

def print_divider(title: str = ""):
    """Print a divider line with optional title."""
    width = 80
    if title:
        print(f"\n{'-' * ((width - len(title) - 4) // 2)} {title} {'-' * ((width - len(title) - 4) // 2)}\n")
    else:
        print(f"\n{'-' * width}\n")

def main():
    """
    Main function to demonstrate the NASA agent with mocked API responses.
    """
    print_divider("NASA TECHNOLOGY AGENT MOCK TEST")
    
    # Set up mocks
    setup_mock_nasa_apis()
    mock_client = setup_mock_anthropic()
    
    print("Initializing NASA agent with mocked API responses...\n")
    
    # Initialize the NASA agent with a mock API key
    agent = NASAAgent(api_key="mock-key-not-used")
    
    # Test queries to demonstrate the agent's capabilities
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
        
        # Process the query
        print("\nProcessing...\n")
        response = agent.process_message(query, verbose=True)
        
        print(f"\nAGENT RESPONSE: {response}")
        print(f"\nAPI Call Count: {mock_client.messages.create.call_count}")
    
    print_divider()
    print("Mock test completed successfully!")
    
    # Stop patches
    patent_api_patch.stop()
    software_api_patch.stop()
    spinoff_api_patch.stop()
    anthropic_patch.stop()

if __name__ == "__main__":
    main()