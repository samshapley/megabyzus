#!/usr/bin/env python3
"""
arXiv API Utilities

This module provides common utilities and helper functions for interacting with
the arXiv API across all endpoint-specific modules.
"""

import os
import json
import time
import logging
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Constants
ARXIV_QUERY_API_URL = "http://export.arxiv.org/api/query"
ARXIV_OAI_PMH_URL = "https://oaipmh.arxiv.org/oai"
RESULTS_DIR = "results"
REQUEST_DELAY = 3.0  # Delay between API requests in seconds (arXiv recommends 3s)

# Create namespace dictionary for XML parsing
NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
    'oai': 'http://www.openarchives.org/OAI/2.0/',
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/'
}

# Set up logging
def setup_logging(log_filename="arxiv_api.log"):
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

def remove_duplicates(results_list, id_field='id'):
    """
    Remove duplicate records from a list of results based on their IDs.
    
    Args:
        results_list (list): List of result records
        id_field (str): The field containing the unique identifier
        
    Returns:
        list: Deduplicated results
    """
    unique_ids = set()
    unique_results = []
    
    for result in results_list:
        result_id = result.get(id_field)
        
        if result_id and result_id not in unique_ids:
            unique_ids.add(result_id)
            unique_results.append(result)
    
    return unique_results

def make_api_request(url, params=None):
    """
    Make a request to the arXiv API with error handling.
    
    Args:
        url (str): The URL to request
        params (dict): Optional parameters for the request
        
    Returns:
        str: The response text or None if there was an error
    """
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"Error fetching data from {url}: HTTP {response.status_code}")
            return None
            
        return response.text
    except Exception as e:
        logger.error(f"Exception when fetching data from {url}: {e}")
        return None

def make_oai_pmh_request(verb, **params):
    """
    Make a request to the arXiv OAI-PMH API.
    
    Args:
        verb (str): The OAI-PMH verb (e.g., 'Identify', 'ListRecords')
        **params: Additional parameters for the OAI-PMH request
        
    Returns:
        str: The response text or None if there was an error
    """
    params['verb'] = verb
    url = ARXIV_OAI_PMH_URL
    
    return make_api_request(url, params)

def parse_atom_response(response_text):
    """
    Parse an Atom XML response from the arXiv API.
    
    Args:
        response_text (str): The XML response text
        
    Returns:
        dict: Parsed response data or None if parsing failed
    """
    try:
        root = ET.fromstring(response_text)
        
        # Parse opensearch metadata
        total_results = root.find('./opensearch:totalResults', NAMESPACES)
        start_index = root.find('./opensearch:startIndex', NAMESPACES)
        items_per_page = root.find('./opensearch:itemsPerPage', NAMESPACES)
        
        metadata = {
            'total_results': int(total_results.text) if total_results is not None else 0,
            'start_index': int(start_index.text) if start_index is not None else 0,
            'items_per_page': int(items_per_page.text) if items_per_page is not None else 0
        }
        
        # Parse entries
        entries = []
        for entry in root.findall('./atom:entry', NAMESPACES):
            entry_data = parse_atom_entry(entry)
            if entry_data:
                entries.append(entry_data)
        
        return {
            'metadata': metadata,
            'entries': entries,
            'count': len(entries),
            'date_collected': generate_timestamp()
        }
    except Exception as e:
        logger.error(f"Error parsing Atom response: {e}")
        return None

def parse_atom_entry(entry):
    """
    Parse an Atom entry element.
    
    Args:
        entry (ET.Element): The entry XML element
        
    Returns:
        dict: Parsed entry data or None if parsing failed
    """
    try:
        # Basic metadata
        entry_id = entry.find('./atom:id', NAMESPACES)
        title = entry.find('./atom:title', NAMESPACES)
        summary = entry.find('./atom:summary', NAMESPACES)
        published = entry.find('./atom:published', NAMESPACES)
        updated = entry.find('./atom:updated', NAMESPACES)
        
        # Extract arXiv ID from URL
        id_text = entry_id.text if entry_id is not None else ""
        arxiv_id = id_text.split('/')[-1] if 'arxiv.org' in id_text else id_text
        
        # Authors
        authors = []
        for author_elem in entry.findall('./atom:author', NAMESPACES):
            name = author_elem.find('./atom:name', NAMESPACES)
            if name is not None:
                authors.append(name.text)
        
        # Links
        links = []
        for link in entry.findall('./atom:link', NAMESPACES):
            link_data = {
                'href': link.get('href'),
                'rel': link.get('rel', ''),
                'type': link.get('type', '')
            }
            links.append(link_data)
        
        # arXiv specific metadata
        categories = []
        for cat in entry.findall('./atom:category', NAMESPACES):
            term = cat.get('term')
            if term:
                categories.append(term)
        
        comment = entry.find('./arxiv:comment', NAMESPACES)
        journal_ref = entry.find('./arxiv:journal_ref', NAMESPACES)
        doi = entry.find('./arxiv:doi', NAMESPACES)
        
        return {
            'id': arxiv_id,
            'title': title.text if title is not None else "",
            'summary': summary.text if summary is not None else "",
            'published': published.text if published is not None else "",
            'updated': updated.text if updated is not None else "",
            'authors': authors,
            'categories': categories,
            'links': links,
            'comment': comment.text if comment is not None else "",
            'journal_ref': journal_ref.text if journal_ref is not None else "",
            'doi': doi.text if doi is not None else ""
        }
    except Exception as e:
        logger.error(f"Error parsing entry: {e}")
        return None

def parse_oai_pmh_response(response_text, metadata_format='oai_dc'):
    """
    Parse an OAI-PMH XML response.
    
    Args:
        response_text (str): The XML response text
        metadata_format (str): The metadata format being used
        
    Returns:
        dict: Parsed response data or None if parsing failed
    """
    try:
        root = ET.fromstring(response_text)
        
        # Check for error
        error = root.find('./oai:error', NAMESPACES)
        if error is not None:
            logger.error(f"OAI-PMH error: {error.text}")
            return None
        
        # Get verb from response
        request = root.find('./oai:request', NAMESPACES)
        verb = request.get('verb') if request is not None else ""
        
        # Process based on verb
        if verb == 'Identify':
            return parse_oai_identify(root)
        elif verb == 'ListRecords' or verb == 'GetRecord':
            return parse_oai_records(root, metadata_format)
        elif verb == 'ListSets':
            return parse_oai_sets(root)
        elif verb == 'ListMetadataFormats':
            return parse_oai_metadata_formats(root)
        elif verb == 'ListIdentifiers':
            return parse_oai_identifiers(root)
        else:
            logger.error(f"Unknown OAI-PMH verb: {verb}")
            return None
    except Exception as e:
        logger.error(f"Error parsing OAI-PMH response: {e}")
        return None
    
def parse_oai_identify(root):
    """
    Parse an OAI-PMH Identify response.
    
    Args:
        root (ET.Element): The root XML element
        
    Returns:
        dict: Parsed Identify data
    """
    identify = root.find('./oai:Identify', NAMESPACES)
    if identify is None:
        return None
    
    repository_name = identify.find('./oai:repositoryName', NAMESPACES)
    base_url = identify.find('./oai:baseURL', NAMESPACES)
    protocol_version = identify.find('./oai:protocolVersion', NAMESPACES)
    earliest_datestamp = identify.find('./oai:earliestDatestamp', NAMESPACES)
    deleted_record = identify.find('./oai:deletedRecord', NAMESPACES)
    granularity = identify.find('./oai:granularity', NAMESPACES)
    
    return {
        'repository_name': repository_name.text if repository_name is not None else "",
        'base_url': base_url.text if base_url is not None else "",
        'protocol_version': protocol_version.text if protocol_version is not None else "",
        'earliest_datestamp': earliest_datestamp.text if earliest_datestamp is not None else "",
        'deleted_record': deleted_record.text if deleted_record is not None else "",
        'granularity': granularity.text if granularity is not None else "",
        'date_collected': generate_timestamp()
    }

def parse_oai_records(root, metadata_format='oai_dc'):
    """
    Parse OAI-PMH ListRecords or GetRecord responses.
    
    Args:
        root (ET.Element): The root XML element
        metadata_format (str): The metadata format being used
        
    Returns:
        dict: Parsed records data
    """
    # Check for resumption token
    resumption_token_elem = root.find('.//oai:resumptionToken', NAMESPACES)
    resumption_token = None
    complete_list_size = None
    cursor = None
    
    if resumption_token_elem is not None:
        resumption_token = resumption_token_elem.text
        complete_list_size = resumption_token_elem.get('completeListSize')
        cursor = resumption_token_elem.get('cursor')
    
    # Parse records
    records = []
    record_nodes = root.findall('.//oai:record', NAMESPACES)
    
    for record in record_nodes:
        parsed_record = parse_oai_record(record, metadata_format)
        if parsed_record:
            records.append(parsed_record)
    
    return {
        'records': records,
        'count': len(records),
        'resumption_token': resumption_token,
        'complete_list_size': int(complete_list_size) if complete_list_size is not None else None,
        'cursor': int(cursor) if cursor is not None else None,
        'date_collected': generate_timestamp()
    }

def parse_oai_record(record, metadata_format='oai_dc'):
    """
    Parse an individual OAI-PMH record.
    
    Args:
        record (ET.Element): The record XML element
        metadata_format (str): The metadata format being used
        
    Returns:
        dict: Parsed record data or None if parsing failed
    """
    try:
        # Get header
        header = record.find('./oai:header', NAMESPACES)
        if header is None:
            return None
        
        identifier = header.find('./oai:identifier', NAMESPACES)
        datestamp = header.find('./oai:datestamp', NAMESPACES)
        
        # Get metadata based on format
        metadata_elem = record.find('./oai:metadata', NAMESPACES)
        metadata = {}
        
        if metadata_elem is not None:
            if metadata_format == 'oai_dc':
                dc = metadata_elem.find('./oai_dc:dc', NAMESPACES)
                if dc is not None:
                    for elem in dc:
                        tag = elem.tag.split('}')[-1]  # Remove namespace
                        if tag in metadata:
                            if isinstance(metadata[tag], list):
                                metadata[tag].append(elem.text)
                            else:
                                metadata[tag] = [metadata[tag], elem.text]
                        else:
                            metadata[tag] = elem.text
            elif metadata_format == 'arXiv' or metadata_format == 'arXivRaw':
                # For arXiv formats, we need custom parsing logic
                # This is a simplified version, actual implementation would need to be more detailed
                for child in metadata_elem:
                    tag = child.tag.split('}')[-1]
                    if child.text and child.text.strip():
                        metadata[tag] = child.text.strip()
            
        return {
            'identifier': identifier.text if identifier is not None else "",
            'datestamp': datestamp.text if datestamp is not None else "",
            'metadata': metadata
        }
    except Exception as e:
        logger.error(f"Error parsing OAI record: {e}")
        return None

def parse_oai_sets(root):
    """
    Parse an OAI-PMH ListSets response.
    
    Args:
        root (ET.Element): The root XML element
        
    Returns:
        dict: Parsed sets data
    """
    sets = []
    set_nodes = root.findall('.//oai:set', NAMESPACES)
    
    for set_node in set_nodes:
        spec = set_node.find('./oai:setSpec', NAMESPACES)
        name = set_node.find('./oai:setName', NAMESPACES)
        
        sets.append({
            'spec': spec.text if spec is not None else "",
            'name': name.text if name is not None else ""
        })
    
    return {
        'sets': sets,
        'count': len(sets),
        'date_collected': generate_timestamp()
    }

def parse_oai_metadata_formats(root):
    """
    Parse an OAI-PMH ListMetadataFormats response.
    
    Args:
        root (ET.Element): The root XML element
        
    Returns:
        dict: Parsed metadata formats data
    """
    formats = []
    format_nodes = root.findall('.//oai:metadataFormat', NAMESPACES)
    
    for format_node in format_nodes:
        prefix = format_node.find('./oai:metadataPrefix', NAMESPACES)
        schema = format_node.find('./oai:schema', NAMESPACES)
        namespace = format_node.find('./oai:metadataNamespace', NAMESPACES)
        
        formats.append({
            'prefix': prefix.text if prefix is not None else "",
            'schema': schema.text if schema is not None else "",
            'namespace': namespace.text if namespace is not None else ""
        })
    
    return {
        'formats': formats,
        'count': len(formats),
        'date_collected': generate_timestamp()
    }

def parse_oai_identifiers(root):
    """
    Parse an OAI-PMH ListIdentifiers response.
    
    Args:
        root (ET.Element): The root XML element
        
    Returns:
        dict: Parsed identifiers data
    """
    identifiers = []
    header_nodes = root.findall('.//oai:header', NAMESPACES)
    
    for header in header_nodes:
        identifier = header.find('./oai:identifier', NAMESPACES)
        datestamp = header.find('./oai:datestamp', NAMESPACES)
        
        identifiers.append({
            'identifier': identifier.text if identifier is not None else "",
            'datestamp': datestamp.text if datestamp is not None else ""
        })
    
    # Check for resumption token
    resumption_token_elem = root.find('.//oai:resumptionToken', NAMESPACES)
    resumption_token = None
    
    if resumption_token_elem is not None:
        resumption_token = resumption_token_elem.text
    
    return {
        'identifiers': identifiers,
        'count': len(identifiers),
        'resumption_token': resumption_token,
        'date_collected': generate_timestamp()
    }

def build_query_string(query_terms):
    """
    Build a query string for the arXiv API.
    
    Args:
        query_terms (dict): Dictionary mapping fields to search terms
        
    Returns:
        str: Formatted query string
    """
    parts = []
    
    for field, terms in query_terms.items():
        if isinstance(terms, list):
            # Multiple terms for the same field
            for term in terms:
                parts.append(f"{field}:{term}")
        else:
            # Single term
            parts.append(f"{field}:{terms}")
    
    return " AND ".join(parts)

def generate_timestamp():
    """
    Generate an ISO format timestamp for the current time.
    
    Returns:
        str: ISO format timestamp
    """
    return datetime.now().isoformat()