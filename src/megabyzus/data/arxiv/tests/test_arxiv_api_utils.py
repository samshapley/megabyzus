#!/usr/bin/env python3
"""
Unit tests for arXiv API utilities module.
"""

import os
import json
import unittest
from unittest import mock
from megabyzus.data.arxiv import arxiv_api_utils as utils

class TestArxivApiUtils(unittest.TestCase):
    """Test cases for arXiv API utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary test directory
        self.test_dir = "test_results"
        utils.RESULTS_DIR = self.test_dir
        
        # Create a test logger
        self.logger = utils.setup_logging("test_log.log")
        
        # Sample Atom XML response
        self.sample_atom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>1</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/2101.12345</id>
    <title>Test Paper Title</title>
    <summary>This is a test summary.</summary>
    <published>2021-01-25T00:00:00Z</published>
    <updated>2021-01-26T00:00:00Z</updated>
    <author>
      <name>Test Author</name>
    </author>
    <author>
      <name>Another Author</name>
    </author>
    <arxiv:comment>Test comment</arxiv:comment>
    <link href="http://arxiv.org/abs/2101.12345v1" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2101.12345v1" rel="related" type="application/pdf"/>
    <category term="cs.AI"/>
    <category term="cs.LG"/>
  </entry>
</feed>"""
        
        # Sample OAI-PMH XML response
        self.sample_oai_pmh_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/
         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>2021-01-01T00:00:00Z</responseDate>
  <request verb="Identify">https://oaipmh.arxiv.org/oai</request>
  <Identify>
    <repositoryName>arXiv</repositoryName>
    <baseURL>https://oaipmh.arxiv.org/oai</baseURL>
    <protocolVersion>2.0</protocolVersion>
    <earliestDatestamp>2007-05-23</earliestDatestamp>
    <deletedRecord>persistent</deletedRecord>
    <granularity>YYYY-MM-DD</granularity>
  </Identify>
</OAI-PMH>"""
    
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
            "entries": [{"id": "test1"}, {"id": "test2"}],
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
            {"id": "id1", "title": "Title 1"},
            {"id": "id2", "title": "Title 2"},
            {"id": "id1", "title": "Title 1 Duplicate"},  # Duplicate ID
            {"id": "id3", "title": "Title 3"}
        ]
        
        # Call the function
        unique_data = utils.remove_duplicates(test_data)
        
        # Check that duplicates were removed
        self.assertEqual(len(unique_data), 3)
        
        # Check that IDs are unique
        unique_ids = set(item["id"] for item in unique_data)
        self.assertEqual(len(unique_ids), 3)
        
        # Check that the first occurrence of each ID was kept
        self.assertEqual(unique_data[0]["id"], "id1")
        self.assertEqual(unique_data[0]["title"], "Title 1")
    
    @mock.patch('requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test successful API request."""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = "Test response"
        mock_get.return_value = mock_response
        
        # Call the function
        result = utils.make_api_request("http://example.com")
        
        # Check that the request was made correctly
        mock_get.assert_called_once_with("http://example.com", params=None)
        
        # Check that the correct data was returned
        self.assertEqual(result, "Test response")
    
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
    
    def test_parse_atom_response(self):
        """Test parsing Atom XML response."""
        # Call the function
        result = utils.parse_atom_response(self.sample_atom_xml)
        
        # Check that the response was parsed correctly
        self.assertIsNotNone(result)
        self.assertEqual(result['metadata']['total_results'], 1)
        self.assertEqual(len(result['entries']), 1)
        self.assertEqual(result['count'], 1)
        
        # Check entry details
        entry = result['entries'][0]
        self.assertEqual(entry['id'], '2101.12345')
        self.assertEqual(entry['title'], 'Test Paper Title')
        self.assertEqual(len(entry['authors']), 2)
        self.assertEqual(entry['authors'][0], 'Test Author')
        self.assertEqual(len(entry['categories']), 2)
        self.assertEqual(entry['categories'][0], 'cs.AI')
    
    def test_parse_oai_pmh_response(self):
        """Test parsing OAI-PMH XML response."""
        # Call the function
        result = utils.parse_oai_pmh_response(self.sample_oai_pmh_xml)
        
        # Check that the response was parsed correctly
        self.assertIsNotNone(result)
        self.assertEqual(result['repository_name'], 'arXiv')
        self.assertEqual(result['protocol_version'], '2.0')
        self.assertEqual(result['earliest_datestamp'], '2007-05-23')
    
    def test_build_query_string(self):
        """Test building query string."""
        # Test data
        test_query = {
            "all": "quantum computing",
            "au": ["Smith", "Jones"],
            "ti": "neural networks"
        }
        
        # Call the function
        query_string = utils.build_query_string(test_query)
        
        # Check the query string
        self.assertIn("all:quantum computing", query_string)
        self.assertIn("au:Smith", query_string)
        self.assertIn("au:Jones", query_string)
        self.assertIn("ti:neural networks", query_string)
        
        # Check that the parts are joined with AND
        parts = query_string.split(" AND ")
        self.assertEqual(len(parts), 4)

if __name__ == "__main__":
    unittest.main()