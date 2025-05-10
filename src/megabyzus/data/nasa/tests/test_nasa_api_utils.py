#!/usr/bin/env python3
"""
Unit tests for NASA API utilities module.
"""

import os
import json
import unittest
from unittest import mock
from agent.data.nasa import nasa_api_utils as utils

class TestNasaApiUtils(unittest.TestCase):
    """Test cases for NASA API utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary test directory
        self.test_dir = "test_results"
        utils.RESULTS_DIR = self.test_dir
        
        # Create a test logger
        self.logger = utils.setup_logging("test_log.log")
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test directory if it exists
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
        
        # Remove test log file if it exists
        if os.path.exists("test_log.log"):
            os.remove("test_log.log")
    
    def test_ensure_results_directory(self):
        """Test that ensure_results_directory creates the directory."""
        # Remove directory if it exists
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
            
        # Call the function
        utils.ensure_results_directory()
        
        # Check that directory was created
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_save_results(self):
        """Test that save_results correctly saves data to a file."""
        # Test data
        test_data = {
            "results": [["id1", "data1"], ["id2", "data2"]],
            "count": 2
        }
        
        # Call the function
        utils.save_results(test_data, "test_data.json")
        
        # Check that the file was created
        filepath = os.path.join(self.test_dir, "test_data.json")
        self.assertTrue(os.path.exists(filepath))
        
        # Check that the file contains the correct data
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
    
    def test_remove_duplicates(self):
        """Test that remove_duplicates correctly removes duplicate records."""
        # Test data with duplicates
        test_data = [
            ["id1", "data1"],
            ["id2", "data2"],
            ["id1", "data1_duplicate"],  # Duplicate ID
            ["id3", "data3"]
        ]
        
        # Call the function
        unique_data = utils.remove_duplicates(test_data)
        
        # Check that duplicates were removed
        self.assertEqual(len(unique_data), 3)
        
        # Check that IDs are unique
        unique_ids = set(item[0] for item in unique_data)
        self.assertEqual(len(unique_ids), 3)
        
        # Check that the first occurrence of each ID was kept
        self.assertEqual(unique_data[0][0], "id1")
        self.assertEqual(unique_data[0][1], "data1")
    
    @mock.patch('requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test successful API request."""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response
        
        # Call the function
        result = utils.make_api_request("http://example.com")
        
        # Check that the request was made correctly
        mock_get.assert_called_once_with("http://example.com", params=None)
        
        # Check that the correct data was returned
        self.assertEqual(result, {"key": "value"})
    
    @mock.patch('requests.get')
    def test_make_api_request_error(self, mock_get):
        """Test API request with error response."""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the function
        result = utils.make_api_request("http://example.com")
        
        # Check that None was returned
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()