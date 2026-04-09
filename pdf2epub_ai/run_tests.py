#!/usr/bin/env python3
"""
Test runner script for PDF to EPUB conversion system
"""

import os
import sys

# Disable LLM for testing
os.environ["LLM_ENABLED"] = "False"

from app.utils.test_case_generator import generate_test_cases
from app.utils.test_runner import TestRunner
from app.utils.test_reporter import TestReporter
from app.utils.logger import logger


def main():
    """
    Main test execution function
    """
    try:
        logger.info("Starting PDF to EPUB test suite")
        
        # Step 1: Generate test cases
        logger.info("Step 1: Generating test cases...")
        test_cases = generate_test_cases()
        logger.info(f"Generated {len(test_cases)} test cases")
        
        # Step 2: Run tests
        logger.info("Step 2: Running test cases...")
        test_runner = TestRunner()
        results = test_runner.run_all_tests()
        logger.info(f"Completed {len(results)} tests")
        
        # Step 3: Generate reports
        logger.info("Step 3: Generating test reports...")
        test_reporter = TestReporter()
        report_paths = test_reporter.generate_report(results)
        
        # Step 4: Print summary
        logger.info("Step 4: Test suite completed")
        logger.info(f"Test reports generated:")
        for format_name, path in report_paths.items():
            logger.info(f"  {format_name}: {path}")
        
        # Count passed and failed tests
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        success_rate = (passed / len(results)) * 100 if results else 0
        
        logger.info(f"\nTest Summary:")
        logger.info(f"Total tests: {len(results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        
        # Exit with appropriate code
        if failed > 0:
            logger.error(f"{failed} test(s) failed")
            sys.exit(1)
        else:
            logger.info("All tests passed!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error running test suite: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
