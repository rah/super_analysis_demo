"""
Test runner for Superannuation Analysis Tool
Runs all unit and integration tests
"""

import unittest
import sys
import os


def run_all_tests():
    """Discover and run all tests"""
    print("=" * 80)
    print("SUPERANNUATION ANALYSIS TOOL - TEST SUITE")
    print("=" * 80)
    print()
    
    # Discover all tests
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 80)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_unit_tests_only():
    """Run only unit tests (test_simulation_engine.py)"""
    print("Running unit tests only...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_simulation_engine')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def run_integration_tests_only():
    """Run only integration tests (test_integration.py)"""
    print("Running integration tests only...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_integration')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def run_quick_tests():
    """Run a quick subset of tests for rapid feedback"""
    print("Running quick test suite...")
    print("(Basic functionality tests only)")
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add specific quick tests
    from test_simulation_engine import TestSimulationEngine, TestConfigurationLoading
    from test_integration import TestEndToEndAnalysis
    
    suite.addTest(TestConfigurationLoading('test_config_file_exists'))
    suite.addTest(TestSimulationEngine('test_engine_initialization'))
    suite.addTest(TestSimulationEngine('test_generate_return_output_type'))
    suite.addTest(TestSimulationEngine('test_simulate_portfolio_positive_investment'))
    suite.addTest(TestSimulationEngine('test_run_monte_carlo_structure'))
    suite.addTest(TestEndToEndAnalysis('test_complete_analysis_workflow'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'unit':
            sys.exit(run_unit_tests_only())
        elif mode == 'integration':
            sys.exit(run_integration_tests_only())
        elif mode == 'quick':
            sys.exit(run_quick_tests())
        elif mode == 'all':
            sys.exit(run_all_tests())
        else:
            print(f"Unknown test mode: {mode}")
            print("Usage: python run_tests.py [all|unit|integration|quick]")
            print("  all         - Run all tests (default)")
            print("  unit        - Run only unit tests")
            print("  integration - Run only integration tests")
            print("  quick       - Run quick subset of tests")
            sys.exit(1)
    else:
        # Default: run all tests
        sys.exit(run_all_tests())
