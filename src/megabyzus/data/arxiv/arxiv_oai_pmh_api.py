#!/usr/bin/env python3
"""
arXiv OAI-PMH API Module

This module provides functions for interacting with the arXiv OAI-PMH API,
allowing for metadata harvesting and repository exploration.
"""

import time
from megabyzus.data.arxiv import arxiv_api_utils as utils

# Set up logging
logger = utils.setup_logging("arxiv_oai_pmh_api.log")

def identify_repository(save_results=True, filename="arxiv_repository_identify.json"):
    """
    Identify the arXiv OAI-PMH repository.
    
    Args:
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Repository identification data
    """
    logger.info("Identifying arXiv OAI-PMH repository")
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("Identify")
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text)
    
    # Save the results if requested
    if save_results and result_data:
        utils.save_results(result_data, filename)
    
    return result_data

def list_metadata_formats(save_results=True, filename="arxiv_metadata_formats.json"):
    """
    List available metadata formats from the arXiv OAI-PMH repository.
    
    Args:
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Available metadata formats
    """
    logger.info("Listing metadata formats from arXiv OAI-PMH repository")
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("ListMetadataFormats")
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text)
    
    # Save the results if requested
    if save_results and result_data:
        utils.save_results(result_data, filename)
    
    return result_data

def list_sets(save_results=True, filename="arxiv_sets.json"):
    """
    List available sets from the arXiv OAI-PMH repository.
    
    Args:
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Available sets
    """
    logger.info("Listing sets from arXiv OAI-PMH repository")
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("ListSets")
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text)
    
    # Save the results if requested
    if save_results and result_data:
        utils.save_results(result_data, filename)
    
    return result_data

def list_identifiers(metadata_prefix="oai_dc", from_date=None, until_date=None, set_spec=None, save_results=True, filename=None):
    """
    List identifiers from the arXiv OAI-PMH repository.
    
    Args:
        metadata_prefix (str): Metadata format prefix
        from_date (str): Optional start date (YYYY-MM-DD)
        until_date (str): Optional end date (YYYY-MM-DD)
        set_spec (str): Optional set specification
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Available identifiers
    """
    logger.info(f"Listing identifiers from arXiv OAI-PMH repository (set: {set_spec}, from: {from_date}, until: {until_date})")
    
    # Build parameters
    params = {
        "metadataPrefix": metadata_prefix
    }
    
    if from_date:
        params["from"] = from_date
    
    if until_date:
        params["until"] = until_date
    
    if set_spec:
        params["set"] = set_spec
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("ListIdentifiers", **params)
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text)
    
    # Save the results if requested
    if save_results and result_data:
        if not filename:
            set_part = f"_{set_spec}" if set_spec else ""
            date_part = f"_{from_date}-{until_date}" if from_date and until_date else ""
            filename = f"arxiv_identifiers{set_part}{date_part}.json"
        
        utils.save_results(result_data, filename)
    
    return result_data

def get_record(identifier, metadata_prefix="oai_dc", save_results=True, filename=None):
    """
    Get a specific record from the arXiv OAI-PMH repository.
    
    Args:
        identifier (str): OAI-PMH identifier
        metadata_prefix (str): Metadata format prefix
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Record data
    """
    logger.info(f"Getting record {identifier} from arXiv OAI-PMH repository")
    
    # Build parameters
    params = {
        "identifier": identifier,
        "metadataPrefix": metadata_prefix
    }
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("GetRecord", **params)
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text)
    
    # Save the results if requested
    if save_results and result_data:
        if not filename:
            # Extract a clean identifier part for the filename
            id_part = identifier.split(':')[-1].replace('/', '_')
            filename = f"arxiv_record_{id_part}.json"
        
        utils.save_results(result_data, filename)
    
    return result_data

def list_records(metadata_prefix="oai_dc", from_date=None, until_date=None, set_spec=None, save_results=True, filename=None):
    """
    List records from the arXiv OAI-PMH repository.
    
    Args:
        metadata_prefix (str): Metadata format prefix
        from_date (str): Optional start date (YYYY-MM-DD)
        until_date (str): Optional end date (YYYY-MM-DD)
        set_spec (str): Optional set specification
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Records data
    """
    logger.info(f"Listing records from arXiv OAI-PMH repository (set: {set_spec}, from: {from_date}, until: {until_date})")
    
    # Build parameters
    params = {
        "metadataPrefix": metadata_prefix
    }
    
    if from_date:
        params["from"] = from_date
    
    if until_date:
        params["until"] = until_date
    
    if set_spec:
        params["set"] = set_spec
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("ListRecords", **params)
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text, metadata_prefix)
    
    # Save the results if requested
    if save_results and result_data:
        if not filename:
            set_part = f"_{set_spec}" if set_spec else ""
            date_part = f"_{from_date}-{until_date}" if from_date and until_date else ""
            filename = f"arxiv_records{set_part}{date_part}.json"
        
        utils.save_results(result_data, filename)
    
    return result_data

def harvest_records_with_token(resumption_token, metadata_prefix="oai_dc", save_results=True, filename=None):
    """
    Harvest records using a resumption token.
    
    Args:
        resumption_token (str): OAI-PMH resumption token
        metadata_prefix (str): Metadata format prefix
        save_results (bool): Whether to save the results to a file
        filename (str): Optional filename to save results to
        
    Returns:
        dict: Records data
    """
    logger.info(f"Harvesting records with resumption token: {resumption_token}")
    
    # Build parameters
    params = {
        "resumptionToken": resumption_token
    }
    
    # Make the OAI-PMH request
    response_text = utils.make_oai_pmh_request("ListRecords", **params)
    if not response_text:
        return None
    
    # Parse the OAI-PMH response
    result_data = utils.parse_oai_pmh_response(response_text, metadata_prefix)
    
    # Save the results if requested
    if save_results and result_data:
        if not filename:
            token_part = resumption_token[:20].replace(':', '_').replace('/', '_')
            filename = f"arxiv_records_token_{token_part}.json"
        
        utils.save_results(result_data, filename)
    
    return result_data

def harvest_records_complete(metadata_prefix="oai_dc", from_date=None, until_date=None, set_spec=None, max_batches=10, save_results=True, base_filename=None):
    """
    Harvest complete records from the arXiv OAI-PMH repository, handling resumption tokens.
    
    Args:
        metadata_prefix (str): Metadata format prefix
        from_date (str): Optional start date (YYYY-MM-DD)
        until_date (str): Optional end date (YYYY-MM-DD)
        set_spec (str): Optional set specification
        max_batches (int): Maximum number of batches to retrieve
        save_results (bool): Whether to save the results to files
        base_filename (str): Base filename for saved results
        
    Returns:
        dict: Aggregated records data
    """
    logger.info(f"Starting complete harvest of arXiv records (set: {set_spec}, from: {from_date}, until: {until_date}, max_batches: {max_batches})")
    
    all_records = []
    batch = 0
    resumption_token = None
    total_records = None
    
    # First request without resumption token
    result = list_records(
        metadata_prefix=metadata_prefix,
        from_date=from_date,
        until_date=until_date,
        set_spec=set_spec,
        save_results=save_results and base_filename is not None,
        filename=f"{base_filename}_batch{batch+1}.json" if base_filename else None
    )
    
    if not result:
        logger.error("Initial harvest request failed")
        return None
    
    # Add records from first batch
    all_records.extend(result.get('records', []))
    
    # Check for resumption token and total size
    resumption_token = result.get('resumption_token')
    complete_list_size = result.get('complete_list_size')
    
    if complete_list_size:
        total_records = complete_list_size
        logger.info(f"Total records to harvest: {total_records}")
    
    batch += 1
    
    # Continue with resumption tokens until done or max batches reached
    while resumption_token and batch < max_batches:
        logger.info(f"Harvesting batch {batch+1} with resumption token")
        
        # Add delay to respect rate limits
        time.sleep(utils.REQUEST_DELAY)
        
        # Make request with resumption token
        result = harvest_records_with_token(
            resumption_token,
            metadata_prefix=metadata_prefix,
            save_results=save_results and base_filename is not None,
            filename=f"{base_filename}_batch{batch+1}.json" if base_filename else None
        )
        
        if not result:
            logger.error(f"Harvest request failed at batch {batch+1}")
            break
        
        # Add records from this batch
        all_records.extend(result.get('records', []))
        
        # Update resumption token
        resumption_token = result.get('resumption_token')
        
        batch += 1
        
        # Check if we've reached the end
        if not resumption_token:
            logger.info("Reached end of records (no more resumption tokens)")
    
    # Create aggregated result
    if all_records:
        aggregated_result = {
            'records': all_records,
            'count': len(all_records),
            'total_records': total_records,
            'batches_retrieved': batch,
            'metadata_prefix': metadata_prefix,
            'set': set_spec,
            'from_date': from_date,
            'until_date': until_date,
            'date_collected': utils.generate_timestamp()
        }
        
        # Save aggregated results if requested
        if save_results and base_filename:
            utils.save_results(aggregated_result, f"{base_filename}_aggregated.json")
        
        logger.info(f"Complete harvest finished: {len(all_records)} records retrieved in {batch} batches")
        return aggregated_result
    
    logger.error("No records were retrieved in the harvest")
    return None

def harvest_by_category(category, metadata_prefix="oai_dc", from_date=None, until_date=None, max_batches=5, save_results=True, base_filename=None):
    """
    Harvest records for a specific arXiv category.
    
    Args:
        category (str): arXiv category (e.g., 'cs', 'physics')
        metadata_prefix (str): Metadata format prefix
        from_date (str): Optional start date (YYYY-MM-DD)
        until_date (str): Optional end date (YYYY-MM-DD)
        max_batches (int): Maximum number of batches to retrieve
        save_results (bool): Whether to save the results to files
        base_filename (str): Base filename for saved results
        
    Returns:
        dict: Harvested records data
    """
    logger.info(f"Harvesting records for category: {category}")
    
    # Construct the set spec
    set_spec = category
    
    # Use a descriptive base filename if none provided
    if save_results and not base_filename:
        date_part = f"_{from_date}-{until_date}" if from_date and until_date else ""
        base_filename = f"arxiv_harvest_{category}{date_part}"
    
    # Perform the harvest
    return harvest_records_complete(
        metadata_prefix=metadata_prefix,
        from_date=from_date,
        until_date=until_date,
        set_spec=set_spec,
        max_batches=max_batches,
        save_results=save_results,
        base_filename=base_filename
    )

def harvest_recent(days=7, categories=None, metadata_prefix="oai_dc", max_batches=3, save_results=True, base_filename=None):
    """
    Harvest recent records from the arXiv OAI-PMH repository.
    
    Args:
        days (int): Number of days to look back
        categories (list): Optional list of categories to harvest
        metadata_prefix (str): Metadata format prefix
        max_batches (int): Maximum number of batches per category
        save_results (bool): Whether to save the results to files
        base_filename (str): Base filename for saved results
        
    Returns:
        dict: Aggregated records data
    """
    from datetime import datetime, timedelta
    
    logger.info(f"Harvesting recent records from the last {days} days")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for OAI-PMH (YYYY-MM-DD)
    from_date = start_date.strftime('%Y-%m-%d')
    until_date = end_date.strftime('%Y-%m-%d')
    
    all_records = []
    
    # If categories specified, harvest each one
    if categories:
        for category in categories:
            logger.info(f"Harvesting recent records for category: {category}")
            
            # Create category-specific filename
            category_filename = f"{base_filename}_{category}" if base_filename else None
            
            # Harvest records for this category
            result = harvest_by_category(
                category=category,
                metadata_prefix=metadata_prefix,
                from_date=from_date,
                until_date=until_date,
                max_batches=max_batches,
                save_results=save_results,
                base_filename=category_filename
            )
            
            if result and result.get('records'):
                all_records.extend(result['records'])
            
            # Add delay between categories
            time.sleep(utils.REQUEST_DELAY)
    else:
        # Harvest all recent records without category filter
        result = harvest_records_complete(
            metadata_prefix=metadata_prefix,
            from_date=from_date,
            until_date=until_date,
            max_batches=max_batches,
            save_results=save_results,
            base_filename=base_filename
        )
        
        if result and result.get('records'):
            all_records.extend(result['records'])
    
    # Remove duplicates
    unique_records = utils.remove_duplicates(all_records)
    
    # Create aggregated result
    aggregated_result = {
        'records': unique_records,
        'count': len(unique_records),
        'days': days,
        'from_date': from_date,
        'until_date': until_date,
        'categories': categories,
        'date_collected': utils.generate_timestamp()
    }
    
    # Save aggregated results if requested
    if save_results and base_filename:
        utils.save_results(aggregated_result, f"{base_filename}_recent_aggregated.json")
    
    logger.info(f"Recent records harvest complete: {len(unique_records)} unique records retrieved")
    return aggregated_result