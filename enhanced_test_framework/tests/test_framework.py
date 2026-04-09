import unittest
import time
import os
import shutil
from enhanced_test_framework.test_case import TestCase
from enhanced_test_framework.test_runner import TestRunner
from enhanced_test_framework.test_reporter import TestReporter
from enhanced_test_framework.test_result import TestResult


class TestEnhancedTestFramework(unittest.TestCase):
    """
    Test cases for the enhanced test framework
    """
    
    def setUp(self):
        """
        Set up test environment
        """
        # Create temporary directories for test output
        self.test_output_dir = "./test_output_test"
        self.test_reports_dir = "./test_reports_test"
        
        # Clean up if they exist
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)
    
    def tearDown(self):
        """
        Clean up test environment
        """
        # Clean up temporary directories
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)
    
    def test_test_case_creation(self):
        """
        Test test case creation
        """
        def test_func():
            return "test result"
        
        test_case = TestCase(
            test_id="test1",
            name="Test Case 1",
            description="Test case 1 description",
            test_function=test_func,
            dependencies=[],
            tags=["unit", "test"]
        )
        
        self.assertEqual(test_case.test_id, "test1")
        self.assertEqual(test_case.name, "Test Case 1")
        self.assertEqual(test_case.description, "Test case 1 description")
        self.assertEqual(test_case.dependencies, [])
        self.assertEqual(test_case.tags, ["unit", "test"])
        self.assertEqual(test_case.run(), "test result")
    
    def test_test_result_creation(self):
        """
        Test test result creation
        """
        result = TestResult(
            test_id="test1",
            test_name="Test Case 1",
            success=True,
            message="Test passed",
            duration=1.23,
            output={"key": "value"},
            error=None,
            logs=["Log 1", "Log 2"]
        )
        
        self.assertEqual(result.test_id, "test1")
        self.assertEqual(result.test_name, "Test Case 1")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test passed")
        self.assertAlmostEqual(result.duration, 1.23)
        self.assertEqual(result.output, {"key": "value"})
        self.assertEqual(result.error, None)
        self.assertEqual(result.logs, ["Log 1", "Log 2"])
    
    def test_test_runner_basic(self):
        """
        Test basic test runner functionality
        """
        def test_func():
            time.sleep(0.1)
            return "test result"
        
        test_runner = TestRunner(output_dir=self.test_output_dir, max_workers=2)
        test_runner.add_test_case(TestCase(
            test_id="test1",
            name="Test Case 1",
            description="Test case 1",
            test_function=test_func
        ))
        
        results = test_runner.run_all_tests()
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertAlmostEqual(results[0].duration, 0.1, delta=0.1)
    
    def test_test_runner_dependencies(self):
        """
        Test test runner dependency handling
        """
        dependency_called = False
        
        def dep_func():
            nonlocal dependency_called
            dependency_called = True
            time.sleep(0.1)
            return "dependency result"
        
        def test_func():
            time.sleep(0.1)
            return "test result"
        
        test_runner = TestRunner(output_dir=self.test_output_dir, max_workers=2)
        test_runner.add_test_case(TestCase(
            test_id="dep",
            name="Dependency Test",
            description="Dependency test",
            test_function=dep_func
        ))
        test_runner.add_test_case(TestCase(
            test_id="test",
            name="Test with Dependency",
            description="Test with dependency",
            test_function=test_func,
            dependencies=["dep"]
        ))
        
        results = test_runner.run_all_tests()
        self.assertEqual(len(results), 2)
        self.assertTrue(dependency_called)
        
        # Check that dependency ran before test
        dep_result = next(r for r in results if r.test_id == "dep")
        test_result = next(r for r in results if r.test_id == "test")
        self.assertTrue(dep_result.start_time < test_result.start_time)
    
    def test_test_runner_failed_dependency(self):
        """
        Test test runner handling of failed dependencies
        """
        def dep_func():
            time.sleep(0.1)
            raise Exception("Dependency failed")
        
        def test_func():
            time.sleep(0.1)
            return "test result"
        
        test_runner = TestRunner(output_dir=self.test_output_dir, max_workers=2)
        test_runner.add_test_case(TestCase(
            test_id="dep",
            name="Failing Dependency",
            description="Failing dependency",
            test_function=dep_func
        ))
        test_runner.add_test_case(TestCase(
            test_id="test",
            name="Test with Failing Dependency",
            description="Test with failing dependency",
            test_function=test_func,
            dependencies=["dep"]
        ))
        
        results = test_runner.run_all_tests()
        self.assertEqual(len(results), 2)
        
        # Check that dependency failed
        dep_result = next(r for r in results if r.test_id == "dep")
        self.assertFalse(dep_result.success)
        
        # Check that test was skipped due to failed dependency
        test_result = next(r for r in results if r.test_id == "test")
        self.assertFalse(test_result.success)
        self.assertIn("Skipped due to failed dependencies", test_result.message)
    
    def test_test_runner_timeout(self):
        """
        Test test runner timeout handling
        """
        def long_running_func():
            time.sleep(0.5)
            return "test result"
        
        test_runner = TestRunner(output_dir=self.test_output_dir, max_workers=2)
        test_runner.add_test_case(TestCase(
            test_id="test",
            name="Long Running Test",
            description="Long running test",
            test_function=long_running_func,
            timeout=0.1  # Short timeout
        ))
        
        results = test_runner.run_all_tests()
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIn("Test timed out", results[0].message)
    
    def test_test_reporter(self):
        """
        Test test reporter functionality
        """
        # Create test results
        results = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.23,
                output={"key": "value"},
                logs=["Log 1"]
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=False,
                message="Test failed",
                duration=0.98,
                error="Test error",
                logs=["Log 1", "Log 2"]
            )
        ]
        
        # Generate reports
        test_reporter = TestReporter(output_dir=self.test_reports_dir)
        report_paths = test_reporter.generate_report(results, "test_report")
        
        # Check that reports were generated
        self.assertIn("json", report_paths)
        self.assertIn("html", report_paths)
        self.assertIn("csv", report_paths)
        self.assertTrue(os.path.exists(report_paths["json"]))
        self.assertTrue(os.path.exists(report_paths["html"]))
        self.assertTrue(os.path.exists(report_paths["csv"]))
    
    def test_test_reporter_trend_analysis(self):
        """
        Test test reporter trend analysis functionality
        """
        # Create multiple test runs
        run1 = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.23
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=False,
                message="Test failed",
                duration=0.98,
                error="Test error"
            )
        ]
        
        run2 = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.10
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=True,
                message="Test passed",
                duration=0.85
            )
        ]
        
        run3 = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.05
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=True,
                message="Test passed",
                duration=0.80
            ),
            TestResult(
                test_id="test3",
                test_name="Test 3",
                success=True,
                message="Test passed",
                duration=0.75
            )
        ]
        
        # Analyze trends
        test_reporter = TestReporter(output_dir=self.test_reports_dir)
        trend_data = test_reporter.analyze_trends([run1, run2, run3])
        
        # Check that trend data is generated
        self.assertEqual(trend_data["runs_analyzed"], 3)
        self.assertEqual(len(trend_data["success_rates"]), 3)
        self.assertEqual(len(trend_data["avg_durations"]), 3)
        self.assertIn("trends", trend_data)
    
    def test_test_reporter_run_comparison(self):
        """
        Test test reporter run comparison functionality
        """
        # Create two test runs
        run1 = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.23
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=False,
                message="Test failed",
                duration=0.98,
                error="Test error"
            )
        ]
        
        run2 = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.10
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=True,
                message="Test passed",
                duration=0.85
            ),
            TestResult(
                test_id="test3",
                test_name="Test 3",
                success=False,
                message="Test failed",
                duration=0.75,
                error="New test error"
            )
        ]
        
        # Compare runs
        test_reporter = TestReporter(output_dir=self.test_reports_dir)
        comparison = test_reporter.compare_runs(run1, run2)
        
        # Check that comparison data is generated
        self.assertIn("baseline", comparison)
        self.assertIn("comparison", comparison)
        self.assertIn("changes", comparison)
        self.assertIn("new_failures", comparison)
        self.assertIn("improvements", comparison)
        
        # Check specific values
        self.assertEqual(comparison["new_failures"], ["Test 3"])
        self.assertEqual(comparison["improvements"], ["Test 2"])
    
    def test_test_reporter_enhanced_summary(self):
        """
        Test test reporter enhanced summary statistics
        """
        # Create test results
        results = [
            TestResult(
                test_id="test1",
                test_name="Test 1",
                success=True,
                message="Test passed",
                duration=1.23
            ),
            TestResult(
                test_id="test2",
                test_name="Test 2",
                success=False,
                message="Test failed",
                duration=0.98,
                error="ValueError: Invalid input"
            ),
            TestResult(
                test_id="test3",
                test_name="Test 3",
                success=False,
                message="Test failed",
                duration=1.50,
                error="TypeError: Wrong type"
            )
        ]
        
        # Generate summary
        test_reporter = TestReporter(output_dir=self.test_reports_dir)
        summary = test_reporter._generate_summary(results)
        
        # Check enhanced summary metrics
        self.assertIn("min_duration", summary)
        self.assertIn("max_duration", summary)
        self.assertIn("duration_std_dev", summary)
        self.assertIn("error_distribution", summary)
        
        # Check specific values
        self.assertAlmostEqual(summary["min_duration"], 0.98)
        self.assertAlmostEqual(summary["max_duration"], 1.50)
        self.assertIn("ValueError", summary["error_distribution"])
        self.assertIn("TypeError", summary["error_distribution"])
    
    def test_test_runner_parallel_execution(self):
        """
        Test test runner parallel execution
        """
        start_times = []
        
        def test_func1():
            start_times.append(time.time())
            time.sleep(0.2)
            return "test1 result"
        
        def test_func2():
            start_times.append(time.time())
            time.sleep(0.2)
            return "test2 result"
        
        def test_func3():
            start_times.append(time.time())
            time.sleep(0.2)
            return "test3 result"
        
        test_runner = TestRunner(output_dir=self.test_output_dir, max_workers=3)
        test_runner.add_test_case(TestCase(
            test_id="test1",
            name="Test 1",
            description="Test 1",
            test_function=test_func1
        ))
        test_runner.add_test_case(TestCase(
            test_id="test2",
            name="Test 2",
            description="Test 2",
            test_function=test_func2
        ))
        test_runner.add_test_case(TestCase(
            test_id="test3",
            name="Test 3",
            description="Test 3",
            test_function=test_func3
        ))
        
        start_time = time.time()
        results = test_runner.run_all_tests()
        total_duration = time.time() - start_time
        
        self.assertEqual(len(results), 3)
        # All tests should pass
        for result in results:
            self.assertTrue(result.success)
        # Total duration should be less than sum of individual durations (0.2 * 3 = 0.6)
        self.assertLess(total_duration, 0.6)
        # All start times should be within 0.1 seconds of each other
        if len(start_times) >= 2:
            max_time_diff = max(start_times) - min(start_times)
            self.assertLess(max_time_diff, 0.1)


if __name__ == '__main__':
    unittest.main()
