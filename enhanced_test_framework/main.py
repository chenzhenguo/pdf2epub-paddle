import time
from enhanced_test_framework.test_case import TestCase
from enhanced_test_framework.test_runner import TestRunner
from enhanced_test_framework.test_reporter import TestReporter
from enhanced_test_framework.logger import logger


def test_case_1():
    """Sample test case 1"""
    time.sleep(1)  # Simulate work
    return {"result": "Test 1 passed"}


def test_case_2():
    """Sample test case 2"""
    time.sleep(1.5)  # Simulate work
    return {"result": "Test 2 passed"}


def test_case_3():
    """Sample test case 3 with dependency on test_case_1"""
    time.sleep(0.5)  # Simulate work
    return {"result": "Test 3 passed"}


def test_case_4():
    """Sample test case 4 that fails"""
    time.sleep(0.8)  # Simulate work
    raise Exception("Test 4 failed intentionally")


def test_case_5():
    """Sample test case 5 with dependency on test_case_4 (should be skipped)"""
    time.sleep(0.3)  # Simulate work
    return {"result": "Test 5 passed"}


def test_case_6():
    """Sample test case 6 with timeout"""
    time.sleep(5)  # Simulate long-running test
    return {"result": "Test 6 passed"}


def main():
    """Main function to demonstrate the enhanced test framework"""
    logger.info("Starting enhanced test framework demonstration")
    
    # Create test runner
    test_runner = TestRunner(max_workers=3)
    
    # Add test cases
    test_runner.add_test_case(TestCase(
        test_id="test1",
        name="Sample Test 1",
        description="First sample test case",
        test_function=test_case_1,
        tags=["sample", "basic"]
    ))
    
    test_runner.add_test_case(TestCase(
        test_id="test2",
        name="Sample Test 2",
        description="Second sample test case",
        test_function=test_case_2,
        tags=["sample", "basic"]
    ))
    
    test_runner.add_test_case(TestCase(
        test_id="test3",
        name="Sample Test 3 (depends on test1)",
        description="Third sample test case with dependency",
        test_function=test_case_3,
        dependencies=["test1"],
        tags=["sample", "dependency"]
    ))
    
    test_runner.add_test_case(TestCase(
        test_id="test4",
        name="Sample Test 4 (failing)",
        description="Fourth sample test case that fails",
        test_function=test_case_4,
        tags=["sample", "failing"]
    ))
    
    test_runner.add_test_case(TestCase(
        test_id="test5",
        name="Sample Test 5 (depends on test4)",
        description="Fifth sample test case with dependency on failing test",
        test_function=test_case_5,
        dependencies=["test4"],
        tags=["sample", "dependency"]
    ))
    
    test_runner.add_test_case(TestCase(
        test_id="test6",
        name="Sample Test 6 (timeout)",
        description="Sixth sample test case with timeout",
        test_function=test_case_6,
        timeout=2,  # Set short timeout
        tags=["sample", "timeout"]
    ))
    
    # Run all tests
    logger.info("Running all test cases with parallel execution")
    results = test_runner.run_all_tests()
    
    # Generate summary
    summary = test_runner.generate_summary(results)
    logger.info(f"Test Summary: {summary}")
    
    # Generate reports
    test_reporter = TestReporter()
    report_paths = test_reporter.generate_report(results)
    
    # Print report paths
    logger.info("Test reports generated:")
    for format_name, path in report_paths.items():
        logger.info(f"  {format_name}: {path}")
    
    # Run tests by tags
    logger.info("\nRunning tests by tags: ['sample', 'basic']")
    tagged_results = test_runner.run_tests_by_tags(["sample", "basic"])
    
    # Generate summary for tagged tests
    tagged_summary = test_runner.generate_summary(tagged_results)
    logger.info(f"Tagged Test Summary: {tagged_summary}")
    
    logger.info("Enhanced test framework demonstration completed")


if __name__ == "__main__":
    main()
