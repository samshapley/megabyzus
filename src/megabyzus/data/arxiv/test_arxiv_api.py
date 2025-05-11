#!/usr/bin/env python3
"""
arXiv API Test Script

This script provides a simple demonstration and test of the arXiv API functionality.
Run this script to verify that the implementation works correctly.
"""

import os
import json
import time
import argparse
import logging
from datetime import datetime

# Import the arXiv API modules
from megabyzus.data.arxiv import arxiv_api_utils as utils
from megabyzus.data.arxiv import arxiv_query_api as query_api
from megabyzus.data.arxiv import arxiv_oai_pmh_api as oai_pmh_api

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arxiv_api_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_search_api():
    """
    Test the arXiv Search API functionality.
    """
    logger.info("Testing arXiv Search API...")
    
    # Test basic search
    logger.info("-- Testing basic search")
    result = query_api.search_papers(
        search_query="quantum computing",
        max_results=5,
        save_results=True,
        filename="test_search_quantum.json"
    )
    if not result:
        logger.error("Basic search failed")
        return False
    
    logger.info(f"Search returned {result['count']} results")
    
    # Test search by ID
    logger.info("-- Testing search by ID")
    # Get the ID of the first paper from the previous search
    if result['entries'] and len(result['entries']) > 0:
        paper_id = result['entries'][0]['id']
        paper_result = query_api.get_paper_by_id(
            paper_id=paper_id,
            save_results=True,
            filename="test_paper_by_id.json"
        )
        if not paper_result or not paper_result.get('paper'):
            logger.error(f"Paper retrieval failed for ID: {paper_id}")
            return False
        
        logger.info(f"Successfully retrieved paper: {paper_result['paper']['title']}")
    else:
        logger.warning("Skipping ID search - no papers found in basic search")
    
    # Test search by category
    logger.info("-- Testing search by category")
    category_result = query_api.search_by_category(
        category="cs.AI",
        max_results=5,
        save_results=True,
        filename="test_category_ai.json"
    )
    if not category_result:
        logger.error("Category search failed")
        return False
    
    logger.info(f"Category search returned {category_result['count']} results")
    
    # Test search by author
    logger.info("-- Testing search by author")
    author_result = query_api.search_by_author(
        author_name="Hinton",
        max_results=5,
        save_results=True,
        filename="test_author_hinton.json"
    )
    if not author_result:
        logger.error("Author search failed")
        return False
    
    logger.info(f"Author search returned {author_result['count']} results")
    
    # Test recent papers
    logger.info("-- Testing search for recent papers")
    recent_result = query_api.extract_recent_papers(
        days=7,
        categories=["cs.AI"],
        max_results=5,
        save_results=True,
        filename="test_recent_ai.json"
    )
    if not recent_result:
        logger.error("Recent papers search failed")
        return False
    
    logger.info(f"Recent papers search returned {recent_result['count']} results")
    
    logger.info("Search API tests completed successfully")
    return True

def test_oai_pmh_api():
    """
    Test the arXiv OAI-PMH API functionality.
    """
    logger.info("Testing arXiv OAI-PMH API...")
    
    # Test repository identification
    logger.info("-- Testing repository identification")
    identify_result = oai_pmh_api.identify_repository(
        save_results=True,
        filename="test_identify.json"
    )
    if not identify_result:
        logger.error("Repository identification failed")
        return False
    
    logger.info(f"Identified repository: {identify_result.get('repository_name', 'Unknown')}")
    
    # Test listing metadata formats
    logger.info("-- Testing list metadata formats")
    formats_result = oai_pmh_api.list_metadata_formats(
        save_results=True,
        filename="test_metadata_formats.json"
    )
    if not formats_result:
        logger.error("Listing metadata formats failed")
        return False
    
    logger.info(f"Found {formats_result.get('count', 0)} metadata formats")
    
    # Test listing sets
    logger.info("-- Testing list sets")
    sets_result = oai_pmh_api.list_sets(
        save_results=True,
        filename="test_sets.json"
    )
    if not sets_result:
        logger.error("Listing sets failed")
        return False
    
    logger.info(f"Found {sets_result.get('count', 0)} sets")
    
    # Test listing identifiers (limited to a small set and date range)
    logger.info("-- Testing list identifiers")
    identifiers_result = oai_pmh_api.list_identifiers(
        metadata_prefix="oai_dc",
        set_spec="cs.AI",
        from_date=datetime.now().strftime("%Y-%m-%d"),  # Just today to limit results
        save_results=True,
        filename="test_identifiers.json"
    )
    if not identifiers_result:
        logger.warning("Listing identifiers failed - might be due to no records on today's date")
    else:
        logger.info(f"Found {identifiers_result.get('count', 0)} identifiers")
    
    # Test harvesting records (limited)
    logger.info("-- Testing record harvesting")
    records_result = oai_pmh_api.harvest_by_category(
        category="cs.AI",
        from_date=(datetime.now().strftime("%Y-%m-%d")),  # Just today's records
        max_batches=1,  # Limit to one batch
        save_results=True,
        base_filename="test_harvest"
    )
    if not records_result:
        logger.warning("Harvesting records failed - might be due to no records on today's date")
    else:
        logger.info(f"Harvested {records_result.get('count', 0)} records")
    
    logger.info("OAI-PMH API tests completed")
    return True

def main():
    """
    Main function to run the tests.
    """
    parser = argparse.ArgumentParser(description='Test the arXiv API implementation')
    parser.add_argument('--search-only', action='store_true', help='Only test the search API')
    parser.add_argument('--oai-only', action='store_true', help='Only test the OAI-PMH API')
    parser.add_argument('--results-dir', type=str, default='test_results',
                        help='Directory to store test results')
    args = parser.parse_args()
    
    # Set the results directory
    utils.RESULTS_DIR = args.results_dir
    utils.ensure_results_directory()
    
    # Run the tests
    success = True
    
    if not args.oai_only:
        logger.info("Running Search API tests")
        search_success = test_search_api()
        if not search_success:
            logger.error("Search API tests failed")
            success = False
    
    if not args.search_only:
        # Add a delay to respect rate limits
        time.sleep(utils.REQUEST_DELAY)
        
        logger.info("Running OAI-PMH API tests")
        oai_success = test_oai_pmh_api()
        if not oai_success:
            logger.error("OAI-PMH API tests failed")
            success = False
    
    if success:
        logger.info("All tests passed successfully")
    else:
        logger.error("Some tests failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    main()