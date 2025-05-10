import json
import logging
from typing import List, Dict, Any, Optional, Union
from pydantic import Field

# Import the base Tool class - using absolute imports
from megabyzus.agent.tool_calling_agent import Tool

# Import NASA API modules - using absolute imports
from megabyzus.data.nasa import nasa_patent_api
from megabyzus.data.nasa import nasa_software_api
from megabyzus.data.nasa import nasa_spinoff_api

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("nasa_tools")

# Define Pydantic models for NASA tools

class SearchPatents(Tool):
    """Search for NASA patents matching specific criteria."""
    query: str = Field(
        description="Search term or keywords to find relevant patents."
    )
    center: Optional[str] = Field(
        default=None,
        description="Filter by NASA center (e.g., 'JPL', 'GSFC', 'JSC')."
    )
    max_results: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return (1-50)."
    )

class SearchSoftware(Tool):
    """Search for NASA software matching specific criteria."""
    query: str = Field(
        description="Search term or keywords to find relevant software."
    )
    center: Optional[str] = Field(
        default=None,
        description="Filter by NASA center (e.g., 'JPL', 'GSFC', 'JSC')."
    )
    max_results: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return (1-50)."
    )

class SearchSpinoffs(Tool):
    """Search for NASA spinoff technologies matching specific criteria."""
    query: str = Field(
        description="Search term or keywords to find relevant spinoff technologies."
    )
    center: Optional[str] = Field(
        default=None,
        description="Filter by NASA center (e.g., 'JPL', 'GSFC', 'JSC')."
    )
    max_results: Optional[int] = Field(
        default=10,
        description="Maximum number of results to return (1-50)."
    )

# Generate NASA tools from Pydantic models
nasa_tools = [
    SearchPatents.tool_definition(),
    SearchSoftware.tool_definition(),
    SearchSpinoffs.tool_definition()
]

def format_search_results(results: List[Any], max_results: int) -> List[Dict[str, Any]]:
    """
    Format raw NASA API search results into a more user-friendly structure.
    
    Args:
        results: Raw results from NASA API
        max_results: Maximum number of results to include
        
    Returns:
        Formatted list of results with named fields
    """
    formatted_results = []
    
    # Limit results to max_results
    results_to_process = results[:max_results] if max_results else results
    
    for result in results_to_process:
        # NASA API returns results as arrays, so we convert to named fields
        # The indices are based on the NASA API response structure
        formatted_result = {
            "id": result[0] if len(result) > 0 else "Unknown",
            "case_number": result[1] if len(result) > 1 else "Unknown",
            "title": result[2] if len(result) > 2 else "Unknown",
            "description": result[3] if len(result) > 3 else "Unknown",
            "primary_contact": result[4] if len(result) > 4 else "Unknown",
            "category": result[5] if len(result) > 5 else "Unknown",
            "website": result[6] if len(result) > 6 else "Unknown",
            "status": result[7] if len(result) > 7 else "Unknown",
            "date": result[8] if len(result) > 8 else "Unknown",
            "center": result[9] if len(result) > 9 else "Unknown",
        }
        formatted_results.append(formatted_result)
    
    return formatted_results

def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Process a tool call and return the result as a string.
    
    Args:
        tool_name: The name of the tool to call
        tool_input: The input parameters for the tool
    
    Returns:
        The result of the tool call as a string
    """
    logger.info(f"Processing NASA tool call: {tool_name}")
    logger.info(f"Tool input: {tool_input}")
    
    try:
        if tool_name == "search_patents":
            # Extract parameters with defaults
            query = tool_input.get("query", "")
            center = tool_input.get("center", None)
            max_results = tool_input.get("max_results", 10)
            
            # Validate inputs
            if not query:
                return "Error: Search query is required"
            
            # Log the search
            logger.info(f"Searching patents for: {query}")
            
            # Call the NASA patent API
            # Use save_results=False to avoid writing to files during search
            response_data = nasa_patent_api.search_patents(query, save_results=False)
            
            # Process the results
            if response_data and "results" in response_data:
                raw_results = response_data["results"]
                total_found = len(raw_results)
                
                # Filter by center if specified
                if center:
                    # Center is typically at index 9 in the result array
                    raw_results = [r for r in raw_results if len(r) > 9 and r[9] and center.lower() in r[9].lower()]
                
                # Format the results
                formatted_results = format_search_results(raw_results, max_results)
                
                # Create a response object
                response = {
                    "status": "success",
                    "query": query,
                    "total_found": total_found,
                    "returning": min(max_results, len(formatted_results)),
                    "results": formatted_results
                }
                
                # Return as JSON string
                return json.dumps(response, indent=2)
            else:
                return "Error: Failed to retrieve patent data or no results found"
        
        elif tool_name == "search_software":
            # Extract parameters with defaults
            query = tool_input.get("query", "")
            center = tool_input.get("center", None)
            max_results = tool_input.get("max_results", 10)
            
            # Validate inputs
            if not query:
                return "Error: Search query is required"
            
            # Log the search
            logger.info(f"Searching software for: {query}")
            
            # Call the NASA software API
            response_data = nasa_software_api.search_software(query, save_results=False)
            
            # Process the results
            if response_data and "results" in response_data:
                raw_results = response_data["results"]
                total_found = len(raw_results)
                
                # Filter by center if specified
                if center:
                    # Center is typically at index 9 in the result array
                    raw_results = [r for r in raw_results if len(r) > 9 and r[9] and center.lower() in r[9].lower()]
                
                # Format the results
                formatted_results = format_search_results(raw_results, max_results)
                
                # Create a response object
                response = {
                    "status": "success",
                    "query": query,
                    "total_found": total_found,
                    "returning": min(max_results, len(formatted_results)),
                    "results": formatted_results
                }
                
                # Return as JSON string
                return json.dumps(response, indent=2)
            else:
                return "Error: Failed to retrieve software data or no results found"
        
        elif tool_name == "search_spinoffs":
            # Extract parameters with defaults
            query = tool_input.get("query", "")
            center = tool_input.get("center", None)
            max_results = tool_input.get("max_results", 10)
            
            # Validate inputs
            if not query:
                return "Error: Search query is required"
            
            # Log the search
            logger.info(f"Searching spinoffs for: {query}")
            
            # Call the NASA spinoff API
            response_data = nasa_spinoff_api.search_spinoffs(query, save_results=False)
            
            # Process the results
            if response_data and "results" in response_data:
                raw_results = response_data["results"]
                total_found = len(raw_results)
                
                # Filter by center if specified
                if center:
                    # Center is typically at index 9 in the result array
                    raw_results = [r for r in raw_results if len(r) > 9 and r[9] and center.lower() in r[9].lower()]
                
                # Format the results
                formatted_results = format_search_results(raw_results, max_results)
                
                # Create a response object
                response = {
                    "status": "success",
                    "query": query,
                    "total_found": total_found,
                    "returning": min(max_results, len(formatted_results)),
                    "results": formatted_results
                }
                
                # Return as JSON string
                return json.dumps(response, indent=2)
            else:
                return "Error: Failed to retrieve spinoff data or no results found"
        
        else:
            error_msg = f"Unknown tool '{tool_name}'"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    except Exception as e:
        error_msg = f"An error occurred while processing {tool_name}: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"