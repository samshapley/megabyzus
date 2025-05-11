#!/usr/bin/env python3
"""
Unit tests for arXiv OAI-PMH API module.
"""

import unittest
from unittest import mock
import json
from megabyzus.data.arxiv import arxiv_oai_pmh_api as oai_pmh_api
from megabyzus.data.arxiv import arxiv_api_utils as utils

class TestArxivOaiPmhApi(unittest.TestCase):
    """Test cases for arXiv OAI-PMH API module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test logger
        self.logger = utils.setup_logging("test_oai_pmh_log.log")
        
        # Sample Identify response
        self.sample_identify_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
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
        
        # Sample ListSets response
        self.sample_list_sets_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <responseDate>2021-01-01T00:00:00Z</responseDate>
  <request verb="ListSets">https://oaipmh.arxiv.org/oai</request>
  <ListSets>
    <set>
      <setSpec>cs</setSpec>
      <setName>Computer Science</setName>
    </set>
    <set>
      <setSpec>physics</setSpec>
      <setName>Physics</setName>
    </set>
    <set>
      <setSpec>math</setSpec>
      <setName>Mathematics</setName>
    </set>
  </ListSets>
</OAI-PMH>"""
        
        # Sample ListMetadataFormats response
        self.sample_list_formats_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <responseDate>2021-01-01T00:00:00Z</responseDate>
  <request verb="ListMetadataFormats">https://oaipmh.arxiv.org/oai</request>
  <ListMetadataFormats>
    <metadataFormat>
      <metadataPrefix>oai_dc</metadataPrefix>
      <schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema>
      <metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>
    </metadataFormat>
    <metadataFormat>
      <metadataPrefix>arXiv</metadataPrefix>
      <schema>http://arxiv.org/OAI/arXiv.xsd</schema>
      <metadataNamespace>http://arxiv.org/OAI/arXiv/</metadataNamespace>
    </metadataFormat>
    <metadataFormat>
      <metadataPrefix>arXivRaw</metadataPrefix>
      <schema>http://arxiv.org/OAI/arXivRaw.xsd</schema>
      <metadataNamespace>http://arxiv.org/OAI/arXivRaw/</metadataNamespace>
    </metadataFormat>
  </ListMetadataFormats>
</OAI-PMH>"""
        
        # Sample ListRecords response
        self.sample_list_records_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>2021-01-01T00:00:00Z</responseDate>
  <request verb="ListRecords" metadataPrefix="oai_dc" set="cs">https://oaipmh.arxiv.org/oai</request>
  <ListRecords>
    <record>
      <header>
        <identifier>oai:arXiv.org:2101.12345</identifier>
        <datestamp>2021-01-25</datestamp>
        <setSpec>cs</setSpec>
        <setSpec>cs.AI</setSpec>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Test Paper Title</dc:title>
          <dc:creator>Test Author</dc:creator>
          <dc:subject>Computer Science - Artificial Intelligence</dc:subject>
          <dc:description>This is a test abstract.</dc:description>
          <dc:date>2021-01-25</dc:date>
          <dc:identifier>http://arxiv.org/abs/2101.12345</dc:identifier>
        </oai_dc:dc>
      </metadata>
    </record>
    <record>
      <header>
        <identifier>oai:arXiv.org:2101.54321</identifier>
        <datestamp>2021-01-26</datestamp>
        <setSpec>cs</setSpec>
        <setSpec>cs.CL</setSpec>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Another Test Paper</dc:title>
          <dc:creator>Another Author</dc:creator>
          <dc:subject>Computer Science - Computation and Language</dc:subject>
          <dc:description>This is another test abstract.</dc:description>
          <dc:date>2021-01-26</dc:date>
          <dc:identifier>http://arxiv.org/abs/2101.54321</dc:identifier>
        </oai_dc:dc>
      </metadata>
    </record>
    <resumptionToken cursor="0" completeListSize="156">token12345abcde</resumptionToken>
  </ListRecords>
</OAI-PMH>"""
        
        # Sample GetRecord response
        self.sample_get_record_xml = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <responseDate>2021-01-01T00:00:00Z</responseDate>
  <request verb="GetRecord" identifier="oai:arXiv.org:2101.12345" metadataPrefix="oai_dc">https://oaipmh.arxiv.org/oai</request>
  <GetRecord>
    <record>
      <header>
        <identifier>oai:arXiv.org:2101.12345</identifier>
        <datestamp>2021-01-25</datestamp>
        <setSpec>cs</setSpec>
        <setSpec>cs.AI</setSpec>
      </header>
      <metadata>
        <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
          <dc:title>Test Paper Title</dc:title>
          <dc:creator>Test Author</dc:creator>
          <dc:subject>Computer Science - Artificial Intelligence</dc:subject>
          <dc:description>This is a test abstract.</dc:description>
          <dc:date>2021-01-25</dc:date>
          <dc:identifier>http://arxiv.org/abs/2101.12345</dc:identifier>
        </oai_dc:dc>
      </metadata>
    </record>
  </GetRecord>
</OAI-PMH>"""
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove test log if it exists
        import os
        if os.path.exists("test_oai_pmh_log.log"):
            os.remove("test_oai_pmh_log.log")
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_identify_repository(self, mock_save, mock_parse, mock_request):
        """Test identify_repository functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_identify_xml
        mock_parse.return_value = {
            'repository_name': 'arXiv',
            'base_url': 'https://oaipmh.arxiv.org/oai',
            'protocol_version': '2.0',
            'earliest_datestamp': '2007-05-23',
            'deleted_record': 'persistent',
            'granularity': 'YYYY-MM-DD',
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function
        result = oai_pmh_api.identify_repository()
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with("Identify")
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_identify_xml)
        
        # Verify the results
        self.assertEqual(result['repository_name'], 'arXiv')
        self.assertEqual(result['protocol_version'], '2.0')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_list_metadata_formats(self, mock_save, mock_parse, mock_request):
        """Test list_metadata_formats functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_list_formats_xml
        mock_parse.return_value = {
            'formats': [
                {
                    'prefix': 'oai_dc',
                    'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                    'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/'
                },
                {
                    'prefix': 'arXiv',
                    'schema': 'http://arxiv.org/OAI/arXiv.xsd',
                    'namespace': 'http://arxiv.org/OAI/arXiv/'
                },
                {
                    'prefix': 'arXivRaw',
                    'schema': 'http://arxiv.org/OAI/arXivRaw.xsd',
                    'namespace': 'http://arxiv.org/OAI/arXivRaw/'
                }
            ],
            'count': 3,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function
        result = oai_pmh_api.list_metadata_formats()
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with("ListMetadataFormats")
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_list_formats_xml)
        
        # Verify the results
        self.assertEqual(len(result['formats']), 3)
        self.assertEqual(result['formats'][0]['prefix'], 'oai_dc')
        self.assertEqual(result['formats'][1]['prefix'], 'arXiv')
        self.assertEqual(result['formats'][2]['prefix'], 'arXivRaw')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_list_sets(self, mock_save, mock_parse, mock_request):
        """Test list_sets functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_list_sets_xml
        mock_parse.return_value = {
            'sets': [
                {'spec': 'cs', 'name': 'Computer Science'},
                {'spec': 'physics', 'name': 'Physics'},
                {'spec': 'math', 'name': 'Mathematics'}
            ],
            'count': 3,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function
        result = oai_pmh_api.list_sets()
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with("ListSets")
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_list_sets_xml)
        
        # Verify the results
        self.assertEqual(len(result['sets']), 3)
        self.assertEqual(result['sets'][0]['spec'], 'cs')
        self.assertEqual(result['sets'][0]['name'], 'Computer Science')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_list_records(self, mock_save, mock_parse, mock_request):
        """Test list_records functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_list_records_xml
        mock_parse.return_value = {
            'records': [
                {
                    'identifier': 'oai:arXiv.org:2101.12345',
                    'datestamp': '2021-01-25',
                    'metadata': {
                        'title': 'Test Paper Title',
                        'creator': 'Test Author',
                        'subject': 'Computer Science - Artificial Intelligence',
                        'description': 'This is a test abstract.',
                        'date': '2021-01-25',
                        'identifier': 'http://arxiv.org/abs/2101.12345'
                    }
                },
                {
                    'identifier': 'oai:arXiv.org:2101.54321',
                    'datestamp': '2021-01-26',
                    'metadata': {
                        'title': 'Another Test Paper',
                        'creator': 'Another Author',
                        'subject': 'Computer Science - Computation and Language',
                        'description': 'This is another test abstract.',
                        'date': '2021-01-26',
                        'identifier': 'http://arxiv.org/abs/2101.54321'
                    }
                }
            ],
            'count': 2,
            'resumption_token': 'token12345abcde',
            'complete_list_size': 156,
            'cursor': 0,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function with a set specification
        result = oai_pmh_api.list_records(
            metadata_prefix='oai_dc',
            set_spec='cs',
            from_date='2021-01-01',
            until_date='2021-01-31'
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            "ListRecords",
            metadataPrefix='oai_dc',
            set='cs',
            from='2021-01-01',
            until='2021-01-31'
        )
        
        # Verify the response was parsed with the correct metadata prefix
        mock_parse.assert_called_once_with(self.sample_list_records_xml, 'oai_dc')
        
        # Verify the results
        self.assertEqual(len(result['records']), 2)
        self.assertEqual(result['resumption_token'], 'token12345abcde')
        self.assertEqual(result['complete_list_size'], 156)
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_get_record(self, mock_save, mock_parse, mock_request):
        """Test get_record functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_get_record_xml
        mock_parse.return_value = {
            'records': [
                {
                    'identifier': 'oai:arXiv.org:2101.12345',
                    'datestamp': '2021-01-25',
                    'metadata': {
                        'title': 'Test Paper Title',
                        'creator': 'Test Author',
                        'subject': 'Computer Science - Artificial Intelligence',
                        'description': 'This is a test abstract.',
                        'date': '2021-01-25',
                        'identifier': 'http://arxiv.org/abs/2101.12345'
                    }
                }
            ],
            'count': 1,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function
        result = oai_pmh_api.get_record('oai:arXiv.org:2101.12345', 'oai_dc')
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            "GetRecord",
            identifier='oai:arXiv.org:2101.12345',
            metadataPrefix='oai_dc'
        )
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_get_record_xml)
        
        # Verify the results
        self.assertEqual(len(result['records']), 1)
        self.assertEqual(result['records'][0]['identifier'], 'oai:arXiv.org:2101.12345')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.make_oai_pmh_request')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.parse_oai_pmh_response')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    def test_harvest_records_with_token(self, mock_save, mock_parse, mock_request):
        """Test harvest_records_with_token functionality."""
        # Configure the mocks
        mock_request.return_value = self.sample_list_records_xml
        mock_parse.return_value = {
            'records': [
                {'identifier': 'oai:arXiv.org:2101.12345', 'datestamp': '2021-01-25'},
                {'identifier': 'oai:arXiv.org:2101.54321', 'datestamp': '2021-01-26'}
            ],
            'count': 2,
            'resumption_token': 'nexttoken54321',
            'complete_list_size': 156,
            'cursor': 0,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_save.return_value = True
        
        # Call the function
        result = oai_pmh_api.harvest_records_with_token('token12345abcde', 'oai_dc')
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            "ListRecords",
            resumptionToken='token12345abcde'
        )
        
        # Verify the response was parsed
        mock_parse.assert_called_once_with(self.sample_list_records_xml, 'oai_dc')
        
        # Verify the results
        self.assertEqual(len(result['records']), 2)
        self.assertEqual(result['resumption_token'], 'nexttoken54321')
    
    @mock.patch('megabyzus.data.arxiv.arxiv_oai_pmh_api.list_records')
    @mock.patch('megabyzus.data.arxiv.arxiv_oai_pmh_api.harvest_records_with_token')
    @mock.patch('megabyzus.data.arxiv.arxiv_api_utils.save_results')
    @mock.patch('time.sleep')
    def test_harvest_records_complete(self, mock_sleep, mock_save, mock_harvest_token, mock_list_records):
        """Test harvest_records_complete functionality."""
        # Configure the mocks for initial request
        first_response = {
            'records': [
                {'identifier': 'oai:arXiv.org:2101.12345', 'datestamp': '2021-01-25'},
                {'identifier': 'oai:arXiv.org:2101.54321', 'datestamp': '2021-01-26'}
            ],
            'count': 2,
            'resumption_token': 'token12345abcde',
            'complete_list_size': 4,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_list_records.return_value = first_response
        
        # Configure the mock for token-based request
        second_response = {
            'records': [
                {'identifier': 'oai:arXiv.org:2101.67890', 'datestamp': '2021-01-27'},
                {'identifier': 'oai:arXiv.org:2101.09876', 'datestamp': '2021-01-28'}
            ],
            'count': 2,
            'resumption_token': None,  # No more batches
            'complete_list_size': 4,
            'date_collected': '2021-01-28T00:00:00'
        }
        mock_harvest_token.return_value = second_response
        
        # Call the function
        result = oai_pmh_api.harvest_records_complete(
            metadata_prefix='oai_dc',
            set_spec='cs',
            from_date='2021-01-01',
            until_date='2021-01-31',
            max_batches=5
        )
        
        # Verify the initial request was made correctly
        mock_list_records.assert_called_once_with(
            metadata_prefix='oai_dc',
            set_spec='cs',
            from_date='2021-01-01',
            until_date='2021-01-31',
            save_results=True,
            filename=None
        )
        
        # Verify the token-based request was made
        mock_harvest_token.assert_called_once_with(
            'token12345abcde',
            metadata_prefix='oai_dc',
            save_results=True,
            filename=None
        )
        
        # Verify sleep was called to respect rate limiting
        mock_sleep.assert_called_once()
        
        # Verify the aggregated results
        self.assertEqual(result['count'], 4)  # All 4 records
        self.assertEqual(result['batches_retrieved'], 2)
        self.assertEqual(result['total_records'], 4)
        self.assertEqual(len(result['records']), 4)
    
    @mock.patch('megabyzus.data.arxiv.arxiv_oai_pmh_api.harvest_records_complete')
    def test_harvest_by_category(self, mock_harvest_complete):
        """Test harvest_by_category functionality."""
        # Configure the mock
        mock_harvest_complete.return_value = {
            'records': [
                {'identifier': 'oai:arXiv.org:2101.12345'},
                {'identifier': 'oai:arXiv.org:2101.54321'}
            ],
            'count': 2,
            'batches_retrieved': 1,
            'date_collected': '2021-01-28T00:00:00'
        }
        
        # Call the function
        result = oai_pmh_api.harvest_by_category(
            category='cs.AI',
            from_date='2021-01-01',
            until_date='2021-01-31'
        )
        
        # Verify harvest_records_complete was called with the correct parameters
        mock_harvest_complete.assert_called_once_with(
            metadata_prefix='oai_dc',
            from_date='2021-01-01',
            until_date='2021-01-31',
            set_spec='cs.AI',
            max_batches=5,
            save_results=True,
            base_filename=mock.ANY
        )
        
        # Verify the results were passed through
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['records']), 2)

if __name__ == "__main__":
    unittest.main()