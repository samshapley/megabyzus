#!/usr/bin/env python3
"""
NASA Technology Transfer API Data Collector

This script exhaustively collects all data from the NASA Technology Transfer API
across patents, software, and spinoffs, using pagination to ensure complete data retrieval.
Results are saved to structured JSON files.
"""

import os
import json
import time
import argparse
import logging
from datetime import datetime
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nasa_api_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://technology.nasa.gov/api/query"
API_TYPES = ["patent", "software", "spinoff"]
RESULTS_DIR = "results"
REQUEST_DELAY = 1.0  # Delay between API requests in seconds

# Ensure results directory exists
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
    logger.info(f"Created results directory: {RESULTS_DIR}")

def get_search_terms():
    """
    Get a comprehensive list of search terms to ensure exhaustive data collection.
    Returns a list of search keywords.
    """
    # Basic set of defense-related terms
    defense_terms = [
        "defense", "military", "weapon", "armor", "missile", 
        "radar", "surveillance", "security", "protection", "communication",
        "aerospace", "satellite", "shield", "detection", "stealth",
        "navigation", "propulsion", "sensor", "encryption", "targeting"
    ]
    
    # NASA centers for more comprehensive searches
    nasa_centers = [
        "NASA", "JPL", "GSFC", "JSC", "LARC", "ARC", "GRC", "MSFC", "KSC", "SSC"
    ]
    
    # Technical/scientific terms that might yield relevant results
    technical_terms = [
        "system", "technology", "material", "structure", "device",
        "composite", "module", "algorithm", "network", "computing"
    ]
    
    # Combine all terms
    all_terms = defense_terms + nasa_centers + technical_terms
    
    # Add some comprehensive search terms
    all_terms.extend(["a", "the", "and", "space", "aircraft"])
    
    # Remove duplicates and return
    return list(set(all_terms))

def fetch_api_data(api_type, search_term):
    """
    Fetch all data for a specific API type and search term, handling pagination.
    
    Args:
        api_type (str): The API type ('patent', 'software', or 'spinoff')
        search_term (str): The search term to query
        
    Returns:
        dict: Complete results including all pages
    """
    logger.info(f"Fetching {api_type} data for search term: '{search_term}'")
    
    url = f"{API_BASE_URL}/{api_type}/{search_term}"
    complete_results = []
    page = 0
    total_pages = None
    total_results = None
    
    while True:
        try:
            logger.debug(f"Requesting {url} - page {page}")
            response = requests.get(f"{url}?page={page}")
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Error fetching data: HTTP {response.status_code}")
                break
                
            # Parse the response
            data = response.json()
            
            # Extract results from this page
            results = data.get("results", [])
            complete_results.extend(results)
            
            # Set total results and pages if not already set
            if total_results is None:
                total_results = data.get("total", 0)
                total_pages = (total_results + data.get("perpage", 10) - 1) // data.get("perpage", 10)
                logger.info(f"Found {total_results} total results across {total_pages} pages")
            
            # Log progress
            logger.info(f"Retrieved page {page+1}/{total_pages} ({len(results)} items)")
            
            # Check if we've retrieved all results
            if len(complete_results) >= total_results or not results:
                break
                
            # Move to the next page
            page += 1
            
            # Add a delay to avoid overwhelming the API
            time.sleep(REQUEST_DELAY)
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            break
    
    # Return the complete data
    return {
        "results": complete_results,
        "count": len(complete_results),
        "total": total_results,
        "search_term": search_term,
        "api_type": api_type,
        "date_collected": datetime.now().isoformat()
    }

def save_results(data, api_type, search_term, combined=False):
    """
    Save API results to a JSON file.
    
    Args:
        data (dict): The data to save
        api_type (str): The API type ('patent', 'software', or 'spinoff')
        search_term (str): The search term that was queried
        combined (bool): Whether this is a combined results file
    """
    if combined:
        filename = f"{RESULTS_DIR}/nasa_{api_type}_combined.json"
    else:
        filename = f"{RESULTS_DIR}/nasa_{api_type}_{search_term.replace(' ', '_')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved results to {filename} ({data['count']} items)")
    except Exception as e:
        logger.error(f"Error saving results to {filename}: {e}")

def remove_duplicates(results_list):
    """
    Remove duplicate records from a list of results based on their IDs.
    
    Args:
        results_list (list): List of result records
        
    Returns:
        list: Deduplicated results
    """
    unique_ids = set()
    unique_results = []
    
    for result in results_list:
        # The ID is typically the first element in each result record
        result_id = result[0] if result and len(result) > 0 else None
        
        if result_id and result_id not in unique_ids:
            unique_ids.add(result_id)
            unique_results.append(result)
    
    return unique_results

def collect_data(api_types=None, search_terms=None, combine_results=True):
    """
    Collect data from the NASA Technology Transfer API.
    
    Args:
        api_types (list): List of API types to query
        search_terms (list): List of search terms to use
        combine_results (bool): Whether to combine results into a single file per API type
    """
    if api_types is None:
        api_types = API_TYPES
        
    if search_terms is None:
        search_terms = get_search_terms()
    
    logger.info(f"Starting data collection for {len(api_types)} API types and {len(search_terms)} search terms")
    
    # For each API type, collect and combine data
    for api_type in api_types:
        all_results = []
        
        # Collect data for each search term
        for search_term in search_terms:
            data = fetch_api_data(api_type, search_term)
            
            # Save individual results if requested
            if not combine_results:
                save_results(data, api_type, search_term)
            
            # Add to combined results
            all_results.extend(data.get("results", []))
        
        # If combining results, save the combined file
        if combine_results and all_results:
            # Remove duplicates
            unique_results = remove_duplicates(all_results)
            
            # Create combined data structure
            combined_data = {
                "results": unique_results,
                "count": len(unique_results),
                "total": len(unique_results),
                "api_type": api_type,
                "date_collected": datetime.now().isoformat(),
                "search_terms": search_terms
            }
            
            # Save combined results
            save_results(combined_data, api_type, "combined", combined=True)
            logger.info(f"Combined {api_type} results: {len(all_results)} total, {len(unique_results)} unique")

def main():
    """
    Main function to parse arguments and run the data collection.
    """
    parser = argparse.ArgumentParser(description='Collect data from NASA Technology Transfer API')
    parser.add_argument('--api-types', nargs='+', choices=API_TYPES, 
                        help='Specific API types to query')
    parser.add_argument('--search-terms', nargs='+', 
                        help='Specific search terms to use')
    parser.add_argument('--no-combine', action='store_true', 
                        help='Do not combine results into a single file per API type')
    args = parser.parse_args()
    
    start_time = time.time()
    logger.info("NASA Technology Transfer API Data Collection Started")
    
    collect_data(
        api_types=args.api_types, 
        search_terms=args.search_terms,
        combine_results=not args.no_combine
    )
    
    elapsed_time = time.time() - start_time
    logger.info(f"Data collection completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()