#!/usr/bin/env python3
"""
arXiv Query API Module

This module provides functions for interacting with the arXiv Query API,
allowing for search and retrieval of papers by various criteria.
"""

import time
import urllib.parse
from megabyzus.data.arxiv import arxiv_api_utils as utils

# Set up logging
logger = utils.setup_logging("arxiv_query_api.log")

def search_papers(search_query=None, id_list=None, start=0, max_results=10, sort_by=None, sort_order=None, save_results=True, filename=None):
    """
    Search for papers in the arXiv database using the Query API.
    
    Args:
        search_query (str or dict): Search query string or dictionary of field:term pairs
        id_list (str or list): Comma-separated string or list of arXiv IDs
        start (int): Index of the first returned result
        max_results (int): Maximum number of results to return (max 2000)
        sort_by (str): Field to sort by ('relevance', 'lastUpdatedDate', 'submittedDate')
        sort_order (str): Sort order ('ascending' or 'descending')
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Search results data
    """
    logger.info(f"Searching arXiv papers: query='{search_query}', start={start}, max_results={max_results}")
    
    # Process the search query if it's a dictionary
    if isinstance(search_query, dict):
        search_query = utils.build_query_string(search_query)
    
    # Process ID list if it's a list
    if isinstance(id_list, list):
        id_list = ','.join(id_list)
    
    # Build parameter dictionary
    params = {}
    if search_query:
        params['search_query'] = search_query
    if id_list:
        params['id_list'] = id_list
    
    params['start'] = start
    params['max_results'] = min(max_results, 2000)  # API limit is 2000 per request
    
    if sort_by:
        params['sortBy'] = sort_by
    if sort_order:
        params['sortOrder'] = sort_order
    
    # Make the API request
    response_text = utils.make_api_request(utils.ARXIV_QUERY_API_URL, params)
    if not response_text:
        return None
    
    # Parse the Atom response
    result_data = utils.parse_atom_response(response_text)
    
    if result_data:
        # Add query parameters to the result
        result_data['params'] = params
        
        # Save the results if requested
        if save_results:
            if not filename:
                # Create a filename from the query
                query_part = search_query.replace(':', '_').replace(' ', '_')[:50] if search_query else "all"
                filename = f"arxiv_search_{query_part}_{start}_{max_results}.json"
            
            utils.save_results(result_data, filename)
    
    return result_data

def get_paper_by_id(paper_id, save_results=True, filename=None):
    """
    Get details for a specific paper by its arXiv ID.
    
    Args:
        paper_id (str): The arXiv ID of the paper
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Paper details or None if not found
    """
    logger.info(f"Retrieving paper with ID: {paper_id}")
    
    # Clean the ID (remove version if present)
    clean_id = paper_id.split('v')[0] if 'v' in paper_id else paper_id
    
    # Search for the specific ID
    results = search_papers(id_list=clean_id, save_results=False)
    
    if results and results.get('entries') and len(results['entries']) > 0:
        paper_data = {
            'paper': results['entries'][0],
            'date_collected': utils.generate_timestamp()
        }
        
        # Save the results if requested
        if save_results:
            if not filename:
                filename = f"arxiv_paper_{clean_id}.json"
            
            utils.save_results(paper_data, filename)
        
        return paper_data
    
    logger.error(f"Paper not found: {paper_id}")
    return None

def search_by_category(category, max_results=100, sort_by='submittedDate', sort_order='descending', save_results=True, filename=None):
    """
    Search for papers in a specific arXiv category.
    
    Args:
        category (str): The arXiv category (e.g., 'cs.AI', 'physics.optics')
        max_results (int): Maximum number of results to return (total)
        sort_by (str): Field to sort by
        sort_order (str): Sort order
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Search results data
    """
    logger.info(f"Searching papers in category: {category}")
    
    # Create a search query for the category
    query = f"cat:{category}"
    
    # Make the search request
    return search_papers(
        search_query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=sort_order,
        save_results=save_results,
        filename=filename or f"arxiv_category_{category.replace('.', '_')}.json"
    )

def search_by_author(author_name, max_results=100, sort_by='submittedDate', sort_order='descending', save_results=True, filename=None):
    """
    Search for papers by a specific author.
    
    Args:
        author_name (str): The author name to search for
        max_results (int): Maximum number of results to return
        sort_by (str): Field to sort by
        sort_order (str): Sort order
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Search results data
    """
    logger.info(f"Searching papers by author: {author_name}")
    
    # Create a search query for the author
    # Use au: for exact matches or all: for more general matches
    query = f"au:\"{author_name}\""
    
    # Make the search request
    return search_papers(
        search_query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=sort_order,
        save_results=save_results,
        filename=filename or f"arxiv_author_{author_name.replace(' ', '_')}.json"
    )

def search_with_pagination(search_query, results_per_page=100, max_pages=10, save_results=True, base_filename=None):
    """
    Search for papers with pagination to retrieve more than 2000 results.
    
    Args:
        search_query (str or dict): Search query string or dictionary of field:term pairs
        results_per_page (int): Number of results per page (max 2000)
        max_pages (int): Maximum number of pages to retrieve
        save_results (bool): Whether to save the results to individual files
        base_filename (str): Base filename for saved results
        
    Returns:
        dict: Aggregated search results
    """
    logger.info(f"Performing paginated search: query='{search_query}', results_per_page={results_per_page}, max_pages={max_pages}")
    
    all_entries = []
    page = 0
    start_index = 0
    total_results = None
    
    while page < max_pages:
        logger.info(f"Retrieving page {page+1}")
        
        # Make the API request for this page
        result = search_papers(
            search_query=search_query,
            start=start_index,
            max_results=results_per_page,
            save_results=save_results and base_filename is not None,
            filename=f"{base_filename}_page{page+1}.json" if base_filename else None
        )
        
        if not result or not result.get('entries'):
            break
        
        # Add entries from this page
        all_entries.extend(result['entries'])
        
        # Set total results if not already set
        if total_results is None and 'metadata' in result:
            total_results = result['metadata'].get('total_results', 0)
        
        # Move to the next page
        start_index += results_per_page
        page += 1
        
        # Check if we've retrieved all results
        if start_index >= total_results:
            break
            
        # Add a delay to avoid overwhelming the API
        time.sleep(utils.REQUEST_DELAY)
    
    # Create the aggregated result
    aggregated_result = {
        'entries': all_entries,
        'count': len(all_entries),
        'total_results': total_results,
        'pages_retrieved': page,
        'date_collected': utils.generate_timestamp()
    }
    
    # Save the aggregated results if requested
    if save_results and base_filename:
        utils.save_results(aggregated_result, f"{base_filename}_aggregated.json")
    
    return aggregated_result

def search_multiple_categories(categories, max_results_per_category=100, save_results=True, base_filename=None):
    """
    Search for papers across multiple categories.
    
    Args:
        categories (list): List of arXiv categories to search
        max_results_per_category (int): Maximum results per category
        save_results (bool): Whether to save the results to files
        base_filename (str): Base filename for saved results
        
    Returns:
        dict: Aggregated search results across categories
    """
    logger.info(f"Searching across multiple categories: {categories}")
    
    all_entries = []
    
    for category in categories:
        logger.info(f"Searching category: {category}")
        
        # Search this category
        result = search_by_category(
            category,
            max_results=max_results_per_category,
            save_results=save_results and base_filename is not None,
            filename=f"{base_filename}_{category.replace('.', '_')}.json" if base_filename else None
        )
        
        if result and result.get('entries'):
            all_entries.extend(result['entries'])
        
        # Add a delay between category searches
        time.sleep(utils.REQUEST_DELAY)
    
    # Remove duplicates
    unique_entries = utils.remove_duplicates(all_entries)
    
    # Create the aggregated result
    aggregated_result = {
        'entries': unique_entries,
        'count': len(unique_entries),
        'categories': categories,
        'date_collected': utils.generate_timestamp()
    }
    
    # Save the aggregated results if requested
    if save_results and base_filename:
        utils.save_results(aggregated_result, f"{base_filename}_aggregated.json")
    
    return aggregated_result

def extract_recent_papers(days=1, categories=None, max_results=100, save_results=True, filename=None):
    """
    Extract papers published in the last specified number of days.
    
    Args:
        days (int): Number of days to look back
        categories (list): Optional list of categories to limit search to
        max_results (int): Maximum number of results to return
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Search results data
    """
    logger.info(f"Extracting papers from the last {days} days")
    
    # Build the query for recent papers
    query_parts = []
    
    # Add date constraint
    if days > 0:
        query_parts.append(f"submittedDate:[NOW-{days}DAYS TO NOW]")
    
    # Add category constraint if specified
    if categories:
        if isinstance(categories, list):
            category_queries = [f"cat:{cat}" for cat in categories]
            query_parts.append(f"({' OR '.join(category_queries)})")
        else:
            query_parts.append(f"cat:{categories}")
    
    # Combine the query parts
    query = " AND ".join(query_parts) if query_parts else "*"
    
    # Make the search request
    return search_papers(
        search_query=query,
        max_results=max_results,
        sort_by='submittedDate',
        sort_order='descending',
        save_results=save_results,
        filename=filename or f"arxiv_recent_{days}days.json"
    )