#!/usr/bin/env python3
"""
Script to run the tests.
"""

import sys
import os
import unittest
import argparse

# Add the parent directory to the path so we can import the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_config import setup_logging
from loguru import logger


def run_tests(test_path=None, verbose=False):
    """Run the tests."""
    # Setup logging
    setup_logging()
    
    logger.info("Running tests")
    
    # Discover and run tests
    if test_path:
        # Run specific test file or directory
        if os.path.isfile(test_path):
            # Run specific test file
            test_suite = unittest.defaultTestLoader.discover(
                os.path.dirname(test_path),
                pattern=os.path.basename(test_path)
            )
        else:
            # Run all tests in directory
            test_suite = unittest.defaultTestLoader.discover(test_path)
    else:
        # Run all tests
        test_suite = unittest.defaultTestLoader.discover('tests')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = test_runner.run(test_suite)
    
    # Return success or failure
    return result.wasSuccessful()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the tests')
    parser.add_argument('--path', help='Path to test file or directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Run the tests
    success = run_tests(args.path, args.verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)