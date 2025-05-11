#!/usr/bin/env python3
"""
Unit tests for arXiv Query API module.
"""

import unittest
from unittest import mock
import json
from megabyzus.data.arxiv import arxiv_query_api as query_api
from megabyzus.data.arxiv import arxiv_api_utils as utils

class TestArxivQueryApi(unittest.TestCase):
    """Test cases for arXiv Query API module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test logger
        self.logger = utils.setup_logging("test_query_log.log")
        
        # Sample API response as an Atom feed
        self.sample_response_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>2</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/2101.12345</id>
    <title>Paper One</title>
    <summary>This is the first test paper summary.</summary>
    <published>2021-01-25T00:00:00Z</published>
    <updated>2021-01-26T00:00:00Z</updated>
    <author>
      <name>Author One</name>
    </author>
    <arxiv:comment>Test comment</arxiv:comment>
    <link href="http://arxiv.org/abs/2101.12345v1" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2101.12345v1" rel="related" type="application/pdf"/>
    <category term="cs.AI"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2101.54321</id>
    <title>Paper Two</title>
    <summary>This is the second test paper summary.</summary>
    <published>2021-01-26T00:00:00Z</published>
    <updated>2021-01-27T00:00:00Z</updated>
    <author>
      <name>Author Two</name>
    </author>
    <arxiv:comment>Another test comment</arxiv:comment>
    <link href="http://arxiv.org/abs/2101.54321v1" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2101.54321v1" rel="related" type="application/pdf"/>
    <category term="cs.CL"/>
  </entry>
</feed>"""
        
        # Sample parsed response
        self.sample_parsed_response = {
            'metadata': {
                'total_results': 2,
                'start_index': 0,
                'items_per_page': 10
            },
            'entries': [
                {
                    'id': '2101.12345',
                    'title': 'Paper One',
                    'summary': 'This is the first test paper summary.',
                    'published': '2021-01-25T00:00:00Z',
                    'updated': '2021-01-26T00:00:00Z',
                    'authors': ['Author One'],
                    'categories': ['cs.AI'],
                    'comment': 'Test comment',
                    'links': [
                        {'href': 'http://arxiv.org/abs/2101.12345v1', 'rel': 'alternate', 'type': 'text/html'},
                        {'href': 'http://arxiv.org/pdf/2101.12345v1', 'rel': 'related', 'type': 'application/pdf'}
                    ],
                    'journal_ref': '',
                    'doi': ''
                },
                {
                    'id': '2101.54321',
                    'title': 'Paper Two',
                    'summary': 'This is the second test paper summary.',
                    'published': '2021-01-26T00:00:00Z',
                    'updated': '2021-01-27T00:00:00Z',
                    'authors': ['Author Two'],
                    'categories': ['cs.CL'],
                    'comment': 'Another test comment',
                    'links': [
                        {'href': 'http://arxiv.org/abs/2101.54321v1', 'rel': 'alternate', 'type': 'text/html'},
                        {'href': 'http://arxiv.org/pdf/2101.54321v1', 'rel': 'related', 'type': 'application/pdf'}
                    ],
                    'journal_ref': '',
                    'doi': ''
                }
            ],
            'count': 2,
            'date_collected': '2021-01-28T00:00:00'
        }
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test log if it exists
        import os
        if os.path.exists("test_query_log.log"):
            os.remove("test_query_log.log")
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_api_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_atom_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.generate_timestamp')
    def test_search_papers(self, mock_timestamp, mock_save, mock_parse, mock_request):
        """Test search_papers functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_response_xml
        mock_parse.return_value = self.sample_parsed_response
        mock_save.return_value = True
        mock_timestamp.return_value = '2021-01-28T00:00:00'
        
        # Call the function with basic parameters
        results = query_api.search_papers(
            search_query="quantum computing",
            start=0,
            max_results=10
        )
        
        # Verify the API was called correctly
        mock_request.assert_called_once_with(
            utils.ARXIV_QUERY_API_URL,
            {'search_query': 'quantum computing', 'start': 0, 'max_results': 10}
        )
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_response_xml)
        
        # Verify results were saved
        mock_save.assert_called_once()
        
        # Verify the results structure
        self.assertEqual(results['count'], 2)
        self.assertEqual(len(results['entries']), 2)
        self.assertEqual(results['entries'][0]['id'], '2101.12345')
        self.assertEqual(results['entries'][1]['id'], '2101.54321')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_papers')
    def test_get_paper_by_id(self, mock_search):
        """Test get_paper_by_id functionality."""
        # Configure the mock to return a sample result with one entry
        mock_search.return_value = {
            'entries': [self.sample_parsed_response['entries'][0]],
            'count': 1
        }
        
        # Call the function
        paper = query_api.get_paper_by_id('2101.12345')
        
        # Verify search_papers was called correctly
        mock_search.assert_called_once_with(id_list='2101.12345', save_results=False)
        
        # Verify the result structure
        self.assertIsNotNone(paper)
        self.assertEqual(paper['paper']['id'], '2101.12345')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_papers')
    def test_search_by_category(self, mock_search):
        """Test search_by_category functionality."""
        # Configure the mock
        mock_search.return_value = self.sample_parsed_response
        
        # Call the function
        results = query_api.search_by_category('cs.AI', max_results=50)
        
        # Verify search_papers was called correctly
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        
        self.assertEqual(kwargs['search_query'], 'cat:cs.AI')
        self.assertEqual(kwargs['max_results'], 50)
        
        # Verify the results structure
        self.assertEqual(results, self.sample_parsed_response)
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_papers')
    def test_search_by_author(self, mock_search):
        """Test search_by_author functionality."""
        # Configure the mock
        mock_search.return_value = self.sample_parsed_response
        
        # Call the function
        results = query_api.search_by_author('Einstein', max_results=50)
        
        # Verify search_papers was called correctly
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        
        self.assertEqual(kwargs['search_query'], 'au:"Einstein"')
        self.assertEqual(kwargs['max_results'], 50)
        
        # Verify the results structure
        self.assertEqual(results, self.sample_parsed_response)
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_papers')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_search_with_pagination(self, mock_save, mock_search):
        """Test search_with_pagination functionality."""
        # Configure the first search to return 2 results with a total of 4
        first_response = self.sample_parsed_response.copy()
        first_response['metadata'] = {'total_results': 4, 'start_index': 0, 'items_per_page': 2}
        
        # Configure the second search to return the other 2 results
        second_response = self.sample_parsed_response.copy()
        second_response['metadata'] = {'total_results': 4, 'start_index': 2, 'items_per_page': 2}
        second_response['entries'] = [
            {'id': '2101.67890', 'title': 'Paper Three'},
            {'id': '2101.09876', 'title': 'Paper Four'}
        ]
        second_response['count'] = 2
        
        # Set up the mock to return different responses for first and second calls
        mock_search.side_effect = [first_response, second_response]
        mock_save.return_value = True
        
        # Call the function
        results = query_api.search_with_pagination(
            search_query="neural networks",
            results_per_page=2,
            max_pages=3,
            base_filename="test_pagination"
        )
        
        # Verify search_papers was called twice with different start indices
        self.assertEqual(mock_search.call_count, 2)
        
        # First call should be start=0, max_results=2
        first_call_args = mock_search.call_args_list[0][1]
        self.assertEqual(first_call_args['start'], 0)
        self.assertEqual(first_call_args['max_results'], 2)
        
        # Second call should be start=2, max_results=2
        second_call_args = mock_search.call_args_list[1][1]
        self.assertEqual(second_call_args['start'], 2)
        self.assertEqual(second_call_args['max_results'], 2)
        
        # Verify the aggregated results
        self.assertEqual(results['count'], 4)  # Should have all 4 entries
        self.assertEqual(results['pages_retrieved'], 2)
        self.assertEqual(results['total_results'], 4)
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_by_category')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_search_multiple_categories(self, mock_save, mock_search_category):
        """Test search_multiple_categories functionality."""
        # Configure the mock to return different results for different categories
        category_responses = {
            'cs.AI': {
                'entries': [self.sample_parsed_response['entries'][0]],
                'count': 1
            },
            'cs.CL': {
                'entries': [self.sample_parsed_response['entries'][1]],
                'count': 1
            }
        }
        
        def mock_search_side_effect(category, **kwargs):
            return category_responses.get(category, {'entries': [], 'count': 0})
        
        mock_search_category.side_effect = mock_search_side_effect
        mock_save.return_value = True
        
        # Call the function
        results = query_api.search_multiple_categories(
            categories=['cs.AI', 'cs.CL'],
            max_results_per_category=50,
            base_filename="test_multi_category"
        )
        
        # Verify search_by_category was called for each category
        self.assertEqual(mock_search_category.call_count, 2)
        
        # Verify the aggregated results
        self.assertEqual(results['count'], 2)  # Should have both entries
        self.assertEqual(len(results['entries']), 2)
        self.assertIn('cs.AI', results['categories'])
        self.assertIn('cs.CL', results['categories'])
    
    @mock.patch('megabyzus.data.arxiv.arxiv_query_api.search_papers')
    def test_extract_recent_papers(self, mock_search):
        """Test extract_recent_papers functionality."""
        # Configure the mock
        mock_search.return_value = self.sample_parsed_response
        
        # Call the function without categories
        query_api.extract_recent_papers(days=7)
        
        # Verify search_papers was called correctly
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        
        # Check that the query contains the date constraint
        self.assertIn('submittedDate:[NOW-7DAYS TO NOW]', kwargs['search_query'])
        
        # Reset the mock and test with categories
        mock_search.reset_mock()
        mock_search.return_value = self.sample_parsed_response
        
        # Call the function with categories
        query_api.extract_recent_papers(days=3, categories=['cs.AI', 'cs.CL'])
        
        # Verify search_papers was called correctly
        mock_search.assert_called_once()
        args, kwargs = mock_search.call_args
        
        # Check that the query contains both date and category constraints
        query = kwargs['search_query']
        self.assertIn('submittedDate:[NOW-3DAYS TO NOW]', query)
        self.assertIn('cat:cs.AI', query)
        self.assertIn('cat:cs.CL', query)
        self.assertIn(' OR ', query)  # Categories should be OR'd together
        self.assertIn(' AND ', query)  # Date and category parts should be AND'd

if __name__ == "__main__":
    unittest.main()