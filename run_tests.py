#!/usr/bin/env python
"""
Test runner for Voice AI Agent project.
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all tests in the tests directory."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run tests for a specific module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        # Remove .py extension if present
        if module_name.endswith('.py'):
            module_name = module_name[:-3]
        # Remove test_ prefix if present for matching
        if module_name.startswith('test_'):
            test_name = module_name
        else:
            test_name = f'test_{module_name}'
        exit_code = run_specific_test(test_name)
    else:
        # Run all tests
        exit_code = run_all_tests()

    sys.exit(exit_code)