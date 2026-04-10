import os
import time
import json
import traceback
from typing import List, Dict, Any, Optional
from app.utils.test_case_manager import TestCaseManager
from app.utils.test_runner import TestRunner, TestResult
from app.utils.test_reporter import TestReporter
from app.utils.logger import logger


class TestFlowConfig:
    """
    Test flow configuration class
    """
    def __init__(self, 
                 test_suites: List[str] = None, 
                 max_retries: int = 3, 
                 retry_delay: float = 2.0, 
                 timeout: float = 300.0, 
                 parallel: bool = False, 
                 output_dir: str = "./test_output",
                 report_dir: str = "./test_reports"):
        """
        Initialize test flow configuration
        
        Args:
            test_suites: List of test suites to run
            max_retries: Maximum number of retries for failed tests
            retry_delay: Delay between retries in seconds
            timeout: Timeout for each test in seconds
            parallel: Whether to run tests in parallel
            output_dir: Directory to store test outputs
            report_dir: Directory to store test reports
        """
        self.test_suites = test_suites or ["all"]
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.parallel = parallel
        self.output_dir = output_dir
        self.report_dir = report_dir


class TestFlow:
    """
    Test flow orchestrator class
    """
    def __init__(self, config: TestFlowConfig):
        """
        Initialize test flow
        
        Args:
            config: Test flow configuration
        """
        self.config = config
        self.test_runner = TestRunner(output_dir=config.output_dir)
        self.test_reporter = TestReporter(output_dir=config.report_dir)
        self.test_case_manager = TestCaseManager()
        self.results = []
        self.flow_start_time = 0
        self.flow_end_time = 0
    
    def run(self) -> Dict[str, Any]:
        """
        Run the test flow
        
        Returns:
            Dictionary with flow results and statistics
        """
        try:
            logger.info("Starting test flow execution")
            self.flow_start_time = time.time()
            
            # Run tests based on configured suites
            for suite in self.config.test_suites:
                logger.info(f"Running test suite: {suite}")
                suite_results = self._run_test_suite(suite)
                self.results.extend(suite_results)
            
            # Generate reports
            logger.info("Generating test reports")
            report_paths = self.test_reporter.generate_report(self.results)
            
            self.flow_end_time = time.time()
            flow_duration = self.flow_end_time - self.flow_start_time
            
            # Calculate statistics
            stats = self._calculate_statistics()
            
            # Create flow summary
            summary = {
                "start_time": self.flow_start_time,
                "end_time": self.flow_end_time,
                "duration": flow_duration,
                "statistics": stats,
                "report_paths": report_paths
            }
            
            logger.info(f"Test flow completed in {flow_duration:.2f} seconds")
            logger.info(f"Results: {stats['total']} tests, {stats['passed']} passed, {stats['failed']} failed")
            
            return summary
            
        except Exception as e:
            error_msg = f"Test flow execution failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
    
    def _run_test_suite(self, suite: str) -> List[TestResult]:
        """
        Run a test suite
        
        Args:
            suite: Test suite name
            
        Returns:
            List of test results
        """
        try:
            if suite == "all":
                return self._run_all_tests()
            elif suite == "online":
                return self._run_online_tests()
            elif suite == "local":
                return self._run_local_tests()
            elif suite == "edge_cases":
                return self._run_edge_cases()
            else:
                # Run tests by tags
                return self._run_tests_by_tags([suite])
        except Exception as e:
            error_msg = f"Error running test suite {suite}: {str(e)}"
            logger.error(error_msg)
            return []
    
    def _run_all_tests(self) -> List[TestResult]:
        """
        Run all tests
        
        Returns:
            List of test results
        """
        test_cases = self.test_case_manager.list_test_cases()
        return self._run_with_retry(test_cases)
    
    def _run_online_tests(self) -> List[TestResult]:
        """
        Run online tests
        
        Returns:
            List of test results
        """
        test_cases = self.test_case_manager.get_online_test_cases()
        return self._run_with_retry(test_cases)
    
    def _run_local_tests(self) -> List[TestResult]:
        """
        Run local tests
        
        Returns:
            List of test results
        """
        test_cases = self.test_case_manager.get_local_test_cases()
        return self._run_with_retry(test_cases)
    
    def _run_edge_cases(self) -> List[TestResult]:
        """
        Run edge case tests
        
        Returns:
            List of test results
        """
        test_cases = self.test_case_manager.get_test_case_by_tags(["edge_case"])
        return self._run_with_retry(test_cases)
    
    def _run_tests_by_tags(self, tags: List[str]) -> List[TestResult]:
        """
        Run tests by tags
        
        Args:
            tags: List of tags
            
        Returns:
            List of test results
        """
        test_cases = self.test_case_manager.get_test_case_by_tags(tags)
        return self._run_with_retry(test_cases)
    
    def _run_with_retry(self, test_cases: List) -> List[TestResult]:
        """
        Run test cases with retry mechanism
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        results = []
        
        for test_case in test_cases:
            retries = 0
            last_error = None
            
            while retries <= self.config.max_retries:
                try:
                    result = self.test_runner.run_test_case(test_case)
                    if result.success:
                        results.append(result)
                        break
                    else:
                        last_error = result.error
                        retries += 1
                        if retries <= self.config.max_retries:
                            logger.warning(f"Test {test_case.name} failed, retrying ({retries}/{self.config.max_retries})...")
                            time.sleep(self.config.retry_delay)
                        else:
                            logger.error(f"Test {test_case.name} failed after {self.config.max_retries} retries")
                            results.append(result)
                except Exception as e:
                    last_error = str(e)
                    retries += 1
                    if retries <= self.config.max_retries:
                        logger.warning(f"Test {test_case.name} encountered error, retrying ({retries}/{self.config.max_retries})...")
                        time.sleep(self.config.retry_delay)
                    else:
                        logger.error(f"Test {test_case.name} failed after {self.config.max_retries} retries: {str(e)}")
                        # Create a failed result
                        failed_result = TestResult(
                            test_id=test_case.test_id,
                            test_name=test_case.name,
                            success=False,
                            message=f"Test failed with exception: {str(e)}",
                            duration=0,
                            error=str(e)
                        )
                        results.append(failed_result)
            
        return results
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate test statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0
            }
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        success_rate = (passed / total) * 100 if total > 0 else 0.0
        
        durations = [r.duration for r in self.results]
        average_duration = sum(durations) / total if total > 0 else 0.0
        min_duration = min(durations) if durations else 0.0
        max_duration = max(durations) if durations else 0.0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "average_duration": average_duration,
            "min_duration": min_duration,
            "max_duration": max_duration
        }


def run_test_flow(config: Optional[TestFlowConfig] = None) -> Dict[str, Any]:
    """
    Run test flow with given configuration
    
    Args:
        config: Test flow configuration
        
    Returns:
        Dictionary with flow results and statistics
    """
    if config is None:
        config = TestFlowConfig()
    
    test_flow = TestFlow(config)
    return test_flow.run()


if __name__ == "__main__":
    # Example usage
    config = TestFlowConfig(
        test_suites=["all"],
        max_retries=3,
        retry_delay=2.0,
        timeout=300.0,
        parallel=False,
        output_dir="./test_output",
        report_dir="./test_reports"
    )
    
    result = run_test_flow(config)
    print(json.dumps(result, indent=2))
