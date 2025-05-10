#!/usr/bin/env python3
"""
Test runner for NASA API modules.

This script runs all the unit tests for the NASA API modules.
"""

import unittest
import sys
import os

def run_tests():
    """
    Discover and run all tests in the tests directory.
    
    Returns:
        int: Number of test failures (0 if all tests pass)
    """
    # Add the parent directory to the path so tests can import the modules
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    # Discover all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)

if __name__ == "__main__":
    # Run the tests
    failures = run_tests()
    
    # Exit with non-zero code if there were failures
    sys.exit(failures)