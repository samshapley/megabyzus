#!/usr/bin/env python3
"""
NASA Technology Transfer API Data Collector

This script exhaustively collects all data from the NASA Technology Transfer API
across patents, software, and spinoffs, using multiple search terms and pagination
to ensure complete data retrieval. Results are saved to structured JSON files.
"""

import os
import json
import time
import argparse
import logging
from datetime import datetime

# Import modular endpoint scripts
import megabyzus.data.nasa.nasa_api_utils as utils
import megabyzus.data.nasa.nasa_patent_api
import megabyzus.data.nasa.nasa_software_api
import megabyzus.data.nasa.nasa_spinoff_api

# Set up logging
logger = utils.setup_logging("nasa_api_collector.log")

# Constants
API_TYPES = ["patent", "software", "spinoff"]

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

def collect_all_data(api_types=None, search_terms=None, combine_results=True):
    """
    Collect all data from the NASA Technology Transfer API for specified endpoints
    using multiple search terms to ensure comprehensive data retrieval.
    
    Args:
        api_types (list): List of API types to query (patent, software, spinoff)
        search_terms (list): List of search terms to use (if None, uses get_search_terms())
        combine_results (bool): Whether to combine results into a single file per API type
        
    Returns:
        dict: Summary of results with counts for each API type
    """
    if api_types is None:
        api_types = API_TYPES
        
    if search_terms is None:
        search_terms = get_search_terms()
    
    logger.info(f"Starting comprehensive data collection for {len(api_types)} API types using {len(search_terms)} search terms")
    all_results = {api_type: [] for api_type in api_types}
    
    # For each API type, collect data using multiple search terms
    for api_type in api_types:
        logger.info(f"Collecting {api_type} data using {len(search_terms)} search terms")
        
        # Collect data for each search term
        for search_term in search_terms:
            if api_type == "patent":
                data = nasa_patent_api.search_patents(search_term, save_results=not combine_results)
                all_results[api_type].extend(data.get("results", []))
            
            elif api_type == "software":
                data = nasa_software_api.search_software(search_term, save_results=not combine_results)
                all_results[api_type].extend(data.get("results", []))
            
            elif api_type == "spinoff":
                data = nasa_spinoff_api.search_spinoffs(search_term, save_results=not combine_results)
                all_results[api_type].extend(data.get("results", []))
                
            # Log progress for this search term
            logger.info(f"  - Search term '{search_term}' found {len(data.get('results', []))} {api_type} results")
    
    # If combining results, save the combined files
    if combine_results:
        results_summary = {}
        
        for api_type, results in all_results.items():
            if results:
                # Remove duplicates
                unique_results = utils.remove_duplicates(results)
                results_summary[api_type] = len(unique_results)
                
                # Create combined data structure
                combined_data = {
                    "results": unique_results,
                    "count": len(unique_results),
                    "total": len(unique_results),
                    "api_type": api_type,
                    "date_collected": utils.generate_timestamp(),
                    "search_terms": search_terms
                }
                
                # Save combined results
                filename = f"nasa_{api_type}_combined.json"
                utils.save_results(combined_data, filename)
                logger.info(f"Combined {api_type} results: {len(results)} total, {len(unique_results)} unique")
    else:
        # If not combining results, just return the counts
        results_summary = {api_type: len(results) for api_type, results in all_results.items()}
    
    # Return summary of collected data
    return results_summary

def main():
    """
    Main function to parse arguments and run the data collection.
    """
    parser = argparse.ArgumentParser(description='Collect data from NASA Technology Transfer API')
    parser.add_argument('--api-types', nargs='+', choices=API_TYPES, 
                        help='Specific API types to query (patent, software, spinoff)')
    parser.add_argument('--search-terms', nargs='+', 
                        help='Specific search terms to use (omit to use comprehensive list)')
    parser.add_argument('--no-combine', action='store_true', 
                        help='Do not combine results into a single file per API type')
    parser.add_argument('--single-term', action='store_true', 
                        help='Use only a single generic search term (less comprehensive)')
    args = parser.parse_args()
    
    start_time = time.time()
    logger.info("NASA Technology Transfer API Data Collection Started")
    
    # Ensure results directory exists
    utils.ensure_results_directory()
    
    # Determine search terms
    search_terms = None
    if args.single_term:
        search_terms = ["a"]  # Use only the generic term
        logger.info("Using single generic search term 'a' (less comprehensive)")
    elif args.search_terms:
        search_terms = args.search_terms
        logger.info(f"Using {len(search_terms)} user-specified search terms")
    else:
        search_terms = get_search_terms()
        logger.info(f"Using {len(search_terms)} comprehensive search terms")
    
    # Collect the data
    results_summary = collect_all_data(
        api_types=args.api_types, 
        search_terms=search_terms,
        combine_results=not args.no_combine
    )
    
    # Log summary of results
    for api_type, count in results_summary.items():
        logger.info(f"Collected {count} {api_type} records")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Data collection completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()