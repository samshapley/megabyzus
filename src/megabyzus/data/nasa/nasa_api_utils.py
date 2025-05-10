#!/usr/bin/env python3
"""
NASA Technology Transfer API Utilities

This module provides common utilities and helper functions for interacting with
the NASA Technology Transfer API across all endpoint-specific modules.
"""

import os
import json
import time
import logging
from datetime import datetime
import requests

# Constants
API_BASE_URL = "http://technology.nasa.gov/api/query"
RESULTS_DIR = "results"
REQUEST_DELAY = 1.0  # Delay between API requests in seconds

# Set up logging
def setup_logging(log_filename="nasa_api.log"):
    """
    Set up logging configuration.
    
    Args:
        log_filename (str): Name of the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Create a default logger instance
logger = setup_logging()

def ensure_results_directory():
    """
    Ensure the results directory exists.
    """
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        logger.info(f"Created results directory: {RESULTS_DIR}")

def save_results(data, filename):
    """
    Save API results to a JSON file.
    
    Args:
        data (dict): The data to save
        filename (str): The filename to save to
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    ensure_results_directory()
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved results to {filepath} ({data.get('count', 0)} items)")
        return True
    except Exception as e:
        logger.error(f"Error saving results to {filepath}: {e}")
        return False

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

def make_api_request(url, params=None):
    """
    Make a request to the NASA API with error handling.
    
    Args:
        url (str): The URL to request
        params (dict): Optional parameters for the request
        
    Returns:
        dict: The JSON response or None if there was an error
    """
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Error fetching data from {url}: HTTP {response.status_code}")
            return None
            
        return response.json()
    except Exception as e:
        logger.error(f"Exception when fetching data from {url}: {e}")
        return None

def generate_timestamp():
    """
    Generate an ISO format timestamp for the current time.
    
    Returns:
        str: ISO format timestamp
    """
    return datetime.now().isoformat()