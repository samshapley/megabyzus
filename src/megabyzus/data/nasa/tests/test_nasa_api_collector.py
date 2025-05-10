#!/usr/bin/env python3
"""
Unit tests for the NASA API Collector module.
"""

import unittest
from unittest import mock
import time
from agent.data.nasa import nasa_api_collector as collector
from agent.data.nasa import nasa_api_utils as utils

class TestNasaApiCollector(unittest.TestCase):
    """Test cases for NASA API Collector module."""
    
    def setUp(self):
        """Set up test environment."""
        # Sample patent results
        self.patent_results = {
            "results": [
                ["patent1", "case1", "title1", "description1"],
                ["patent2", "case2", "title2", "description2"]
            ],
            "count": 2,
            "total": 2,
            "api_type": "patent",
            "search_term": "test",
            "date_collected": "2025-01-01T00:00:00"
        }
        
        # Sample software results
        self.software_results = {
            "results": [
                ["software1", "case1", "title1", "description1"],
                ["software2", "case2", "title2", "description2"]
            ],
            "count": 2,
            "total": 2,
            "api_type": "software",
            "search_term": "test",
            "date_collected": "2025-01-01T00:00:00"
        }
        
        # Sample spinoff results
        self.spinoff_results = {
            "results": [
                ["spinoff1", "case1", "title1", "description1"],
                ["spinoff2", "case2", "title2", "description2"]
            ],
            "count": 2,
            "total": 2,
            "api_type": "spinoff",
            "search_term": "test",
            "date_collected": "2025-01-01T00:00:00"
        }
    
    @mock.patch('megabyzus.data.nasa.nasa_patent_api.extract_all_patents')
    @mock.patch('megabyzus.data.nasa.nasa_software_api.extract_all_software')
    @mock.patch('megabyzus.data.nasa.nasa_spinoff_api.extract_all_spinoffs')
    def test_collect_all_data_no_search_term(self, mock_spinoff, mock_software, mock_patent):
        """Test collecting all data without a search term."""
        # Configure the mocks
        mock_patent.return_value = self.patent_results
        mock_software.return_value = self.software_results
        mock_spinoff.return_value = self.spinoff_results
        
        # Call the function with mocked dependencies
        with mock.patch.object(collector, 'utils') as mock_utils:
            mock_utils.remove_duplicates.return_value = self.patent_results["results"]
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.save_results.return_value = True
            
            # Call the collect function
            results = collector.collect_all_data(combine_results=True)
        
        # Verify extract_all functions were called
        mock_patent.assert_called_once_with(save_results=False)
        mock_software.assert_called_once_with(save_results=False)
        mock_spinoff.assert_called_once_with(save_results=False)
        
        # Verify the results summary
        self.assertEqual(results["patent"], 2)
        self.assertEqual(results["software"], 2)
        self.assertEqual(results["spinoff"], 2)
    
    @mock.patch('megabyzus.data.nasa.nasa_patent_api.search_patents')
    @mock.patch('megabyzus.data.nasa.nasa_software_api.search_software')
    @mock.patch('megabyzus.data.nasa.nasa_spinoff_api.search_spinoffs')
    def test_collect_all_data_with_search_term(self, mock_spinoff, mock_software, mock_patent):
        """Test collecting all data with a search term."""
        # Configure the mocks
        mock_patent.return_value = self.patent_results
        mock_software.return_value = self.software_results
        mock_spinoff.return_value = self.spinoff_results
        
        # Call the function with mocked dependencies
        with mock.patch.object(collector, 'utils') as mock_utils:
            mock_utils.remove_duplicates.return_value = self.patent_results["results"]
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.save_results.return_value = True
            
            # Call the collect function with a search term
            results = collector.collect_all_data(search_term="test", combine_results=True)
        
        # Verify search functions were called with the search term
        mock_patent.assert_called_once_with("test", save_results=False)
        mock_software.assert_called_once_with("test", save_results=False)
        mock_spinoff.assert_called_once_with("test", save_results=False)
        
        # Verify the results summary
        self.assertEqual(results["patent"], 2)
        self.assertEqual(results["software"], 2)
        self.assertEqual(results["spinoff"], 2)
    
    @mock.patch('megabyzus.data.nasa.nasa_patent_api.extract_all_patents')
    def test_collect_all_data_specific_api_type(self, mock_patent):
        """Test collecting data for a specific API type."""
        # Configure the mocks
        mock_patent.return_value = self.patent_results
        
        # Call the function with mocked dependencies
        with mock.patch.object(collector, 'utils') as mock_utils:
            mock_utils.remove_duplicates.return_value = self.patent_results["results"]
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.save_results.return_value = True
            
            # Call the collect function for patents only
            results = collector.collect_all_data(api_types=["patent"], combine_results=True)
        
        # Verify only the patent extraction function was called
        mock_patent.assert_called_once_with(save_results=False)
        
        # Verify the results summary includes only patents
        self.assertEqual(len(results), 1)
        self.assertEqual(results["patent"], 2)
        self.assertNotIn("software", results)
        self.assertNotIn("spinoff", results)
    
    @mock.patch('megabyzus.data.nasa.nasa_patent_api.extract_all_patents')
    @mock.patch('megabyzus.data.nasa.nasa_software_api.extract_all_software')
    @mock.patch('megabyzus.data.nasa.nasa_spinoff_api.extract_all_spinoffs')
    def test_collect_all_data_no_combine(self, mock_spinoff, mock_software, mock_patent):
        """Test collecting all data without combining results."""
        # Configure the mocks
        mock_patent.return_value = self.patent_results
        mock_software.return_value = self.software_results
        mock_spinoff.return_value = self.spinoff_results
        
        # Call the function with mocked dependencies
        with mock.patch.object(collector, 'utils') as mock_utils:
            mock_utils.remove_duplicates.return_value = self.patent_results["results"]
            mock_utils.generate_timestamp.return_value = "2025-01-01T00:00:00"
            mock_utils.save_results.return_value = True
            
            # Call the collect function without combining results
            results = collector.collect_all_data(combine_results=False)
        
        # Verify extract_all functions were called with save_results=True
        mock_patent.assert_called_once_with(save_results=True)
        mock_software.assert_called_once_with(save_results=True)
        mock_spinoff.assert_called_once_with(save_results=True)
        
        # Verify utils.save_results was not called (individual scripts handle saving)
        mock_utils.save_results.assert_not_called()

if __name__ == "__main__":
    unittest.main()