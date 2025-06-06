#!/usr/bin/env python3
"""
NASA Patent API Module

This module provides functions for interacting with the NASA Technology Transfer API
specifically for patents, including both targeted searching and complete data extraction.
"""

import time
from megabyzus.data.nasa import nasa_api_utils as utils

# Set up logging
logger = utils.setup_logging("nasa_patent_api.log")

def search_patents(search_term, save_results=True, filename=None):
    """
    Search the NASA Technology Transfer API for patents matching a specific term.
    
    Args:
        search_term (str): Search term to query
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Search results data
    """
    logger.info(f"Searching patents for term: '{search_term}'")
    return fetch_patent_data(search_term, save_results, filename)

def extract_all_patents(save_results=True, filename=None):
    """
    Extract all patent data from the NASA Technology Transfer API using a generic search.
    
    Args:
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Complete patent data
    """
    logger.info("Extracting all patents from NASA Technology Transfer API")
    # Using a search term that will return all patents (the empty string or 'a')
    return fetch_patent_data("a", save_results, filename or "nasa_patents_all.json")

def fetch_patent_data(search_term, save_results=True, filename=None):
    """
    Fetch all patent data for a specific search term, handling pagination.
    
    Args:
        search_term (str): The search term to query
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Complete results including all pages
    """
    api_type = "patent"
    url = f"{utils.API_BASE_URL}/{api_type}/{search_term}"
    complete_results = []
    page = 0
    total_pages = None
    total_results = None
    
    while True:
        logger.debug(f"Requesting {url} - page {page}")
        
        data = utils.make_api_request(f"{url}", params={"page": page})
        if not data:
            break
            
        # Extract results from this page
        results = data.get("results", [])
        complete_results.extend(results)
        
        # Set total results and pages if not already set
        if total_results is None:
            total_results = data.get("total", 0)
            total_pages = (total_results + data.get("perpage", 10) - 1) // data.get("perpage", 10)
            logger.info(f"Found {total_results} total patent results across {total_pages} pages")
        
        # Log progress
        logger.info(f"Retrieved page {page+1}/{total_pages} ({len(results)} items)")
        
        # Check if we've retrieved all results
        if len(complete_results) >= total_results or not results:
            break
            
        # Move to the next page
        page += 1
        
        # Add a delay to avoid overwhelming the API
        time.sleep(utils.REQUEST_DELAY)
        
    # Create the result data structure
    result_data = {
        "results": complete_results,
        "count": len(complete_results),
        "total": total_results,
        "search_term": search_term,
        "api_type": api_type,
        "date_collected": utils.generate_timestamp()
    }
    
    # Save the results if requested
    if save_results:
        if not filename:
            filename = f"nasa_{api_type}_{search_term.replace(' ', '_')}.json"
        utils.save_results(result_data, filename)
    
    return result_data