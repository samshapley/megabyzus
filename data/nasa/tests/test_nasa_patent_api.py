#!/usr/bin/env python3
"""
Unit tests for NASA Patent API module.
"""

import unittest
from unittest import mock
import json
from megabyzus.data.nasa import nasa_patent_api as patent_api
from megabyzus.data.nasa import nasa_api_utils as utils

class TestNasaPatentApi(unittest.TestCase):
    """Test cases for NASA Patent API module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test logger
        self.logger = utils.setup_logging("test_patent_log.log")
        
        # Sample API response
        self.sample_response = {
            "results": [
                ["id1", "case1", "title1", "description1"],
                ["id2", "case2", "title2", "description2"]
            ],
            "total": 2,
            "perpage": 10
        }
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test log if it exists
        import os
        if os.path.exists("test_patent_log.log"):
            os.remove("test_patent_log.log")
    
    @mock.patch('megabyzus.data.nasa.nasa_api_utils.make_api_request')
    def test_search_patents(self, mock_make_request):
        """Test search_patents functionality."""
        # Configure the mock
        mock_make_request.return_value = self.sample_response
        
        # Call the function with mocked dependencies
        with mock.patch.object(patent_api, 'utils') as mock_utils:
            mock_utils.make_api_request = mock_make_request
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.API_BASE_URL = "http://example.com/api"
            mock_utils.REQUEST_DELAY = 0
            
            # Mock save_results to avoid file operations
            mock_utils.save_results.return_value = True
            
            # Call the search function
            results = patent_api.search_patents("test_term", save_results=True, filename="test_output.json")
        
        # Verify the API was called correctly
        mock_make_request.assert_called_once_with("http://example.com/api/patent/test_term", params={'page': 0})
        
        # Verify the results structure
        self.assertEqual(results["count"], 2)
        self.assertEqual(results["total"], 2)
        self.assertEqual(results["search_term"], "test_term")
        self.assertEqual(results["api_type"], "patent")
        self.assertEqual(len(results["results"]), 2)
    
    @mock.patch('megabyzus.data.nasa.nasa_api_utils.make_api_request')
    def test_extract_all_patents(self, mock_make_request):
        """Test extract_all_patents functionality."""
        # Configure the mock
        mock_make_request.return_value = self.sample_response
        
        # Call the function with mocked dependencies
        with mock.patch.object(patent_api, 'utils') as mock_utils:
            mock_utils.make_api_request = mock_make_request
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.API_BASE_URL = "http://example.com/api"
            mock_utils.REQUEST_DELAY = 0
            
            # Mock save_results to avoid file operations
            mock_utils.save_results.return_value = True
            
            # Call the extract function
            results = patent_api.extract_all_patents(save_results=True, filename="test_output.json")
        
        # Verify the API was called correctly
        mock_make_request.assert_called_once_with("http://example.com/api/patent/a", params={'page': 0})
        
        # Verify the results structure
        self.assertEqual(results["count"], 2)
        self.assertEqual(results["total"], 2)
        self.assertEqual(results["search_term"], "a")
        self.assertEqual(results["api_type"], "patent")
        self.assertEqual(len(results["results"]), 2)
    
    @mock.patch('megabyzus.data.nasa.nasa_api_utils.make_api_request')
    def test_fetch_patent_data_pagination(self, mock_make_request):
        """Test fetch_patent_data pagination handling."""
        # Configure the mock to return different responses for different pages
        page1_response = {
            "results": [["id1", "case1", "title1", "description1"]],
            "total": 2,
            "perpage": 1
        }
        
        page2_response = {
            "results": [["id2", "case2", "title2", "description2"]],
            "total": 2,
            "perpage": 1
        }
        
        mock_make_request.side_effect = [page1_response, page2_response]
        
        # Call the function with mocked dependencies
        with mock.patch.object(patent_api, 'utils') as mock_utils:
            mock_utils.make_api_request = mock_make_request
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.API_BASE_URL = "http://example.com/api"
            mock_utils.REQUEST_DELAY = 0
            
            # Mock save_results to avoid file operations
            mock_utils.save_results.return_value = True
            
            # Call the fetch function
            results = patent_api.fetch_patent_data("test_term", save_results=True)
        
        # Verify the API was called for both pages
        self.assertEqual(mock_make_request.call_count, 2)
        
        # Verify the results contain data from both pages
        self.assertEqual(results["count"], 2)
        self.assertEqual(results["total"], 2)
        self.assertEqual(len(results["results"]), 2)
        self.assertEqual(results["results"][0][0], "id1")
        self.assertEqual(results["results"][1][0], "id2")

if __name__ == "__main__":
    unittest.main()