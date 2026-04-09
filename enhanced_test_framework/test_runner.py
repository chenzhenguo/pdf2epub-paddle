import os
import time
import json
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime

from .test_case import TestCase
from .test_result import TestResult
from .logger import logger


class TestRunner:
    """
    Enhanced test runner with parallel execution and dependency management
    """
    def __init__(self, output_dir: str = "./test_output", max_workers: int = 4):
        """
        Initialize test runner
        
        Args:
            output_dir: Directory to store test results and output files
            max_workers: Maximum number of parallel workers
        """
        self.output_dir = output_dir
        self.results_dir = os.path.join(output_dir, "results")
        self.logs_dir = os.path.join(output_dir, "logs")
        
        # Create directories
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.max_workers = max_workers
        self.test_cases = {}
        self.executed_tests = set()
        self.failed_tests = set()
    
    def add_test_case(self, test_case: TestCase):
        """
        Add test case to the runner
        
        Args:
            test_case: TestCase instance
        """
        self.test_cases[test_case.test_id] = test_case
    
    def run_test_case(self, test_case: TestCase) -> TestResult:
        """
        Run a single test case
        
        Args:
            test_case: TestCase instance
            
        Returns:
            TestResult instance
        """
        start_time = time.time()
        logs = []
        
        def log_callback(message: str):
            logs.append(message)
            logger.info(message, test_case.test_id)
        
        try:
            logger.log_test_start(test_case.test_id, test_case.name)
            
            # Run test with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(test_case.run)
                try:
                    output = future.result(timeout=test_case.timeout)
                except concurrent.futures.TimeoutError:
                    error_msg = f"Test timed out after {test_case.timeout} seconds"
                    logger.log_test_error(test_case.test_id, test_case.name, error_msg)
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        success=False,
                        message=error_msg,
                        duration=time.time() - start_time,
                        error=error_msg,
                        logs=logs
                    )
            
            duration = time.time() - start_time
            logger.log_test_end(test_case.test_id, test_case.name, True, duration)
            
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                success=True,
                message="Test passed successfully",
                duration=duration,
                output=output,
                logs=logs
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            duration = time.time() - start_time
            logger.log_test_error(test_case.test_id, test_case.name, error_msg)
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                success=False,
                message=error_msg,
                duration=duration,
                error=error_msg,
                logs=logs
            )
    
    def resolve_dependencies(self, test_id: str) -> List[str]:
        """
        Resolve test dependencies in topological order
        
        Args:
            test_id: Test case ID
            
        Returns:
            List of test IDs in execution order
        """
        resolved = []
        visited = set()
        stack = set()
        
        def dfs(current_id):
            if current_id in stack:
                raise ValueError(f"Circular dependency detected: {current_id}")
            if current_id in visited:
                return
            
            stack.add(current_id)
            test_case = self.test_cases.get(current_id)
            if not test_case:
                raise ValueError(f"Dependency not found: {current_id}")
            
            for dep_id in test_case.dependencies:
                dfs(dep_id)
            
            stack.remove(current_id)
            visited.add(current_id)
            resolved.append(current_id)
        
        dfs(test_id)
        return resolved
    
    def run_test_with_dependencies(self, test_id: str) -> List[TestResult]:
        """
        Run a test case with its dependencies
        
        Args:
            test_id: Test case ID
            
        Returns:
            List of TestResult instances
        """
        results = []
        execution_order = self.resolve_dependencies(test_id)
        
        for current_id in execution_order:
            if current_id in self.executed_tests:
                continue
            
            # Check if any dependency failed
            test_case = self.test_cases[current_id]
            dependency_failed = any(dep in self.failed_tests for dep in test_case.dependencies)
            
            if dependency_failed:
                logger.warning(f"Skipping test {test_case.name} due to failed dependencies", current_id)
                result = TestResult(
                    test_id=current_id,
                    test_name=test_case.name,
                    success=False,
                    message="Skipped due to failed dependencies",
                    duration=0,
                    error="Dependency failure",
                    logs=[f"Skipped due to failed dependencies: {test_case.dependencies}"]
                )
                results.append(result)
                self.failed_tests.add(current_id)
            else:
                result = self.run_test_case(test_case)
                results.append(result)
                self.executed_tests.add(current_id)
                if not result.success:
                    self.failed_tests.add(current_id)
            
            # Save result
            self.save_test_result(result)
        
        return results
    
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all test cases with parallel execution
        
        Returns:
            List of TestResult instances
        """
        results = []
        test_ids = list(self.test_cases.keys())
        
        # Resolve all dependencies first
        all_execution_order = []
        for test_id in test_ids:
            if test_id not in self.executed_tests:
                try:
                    execution_order = self.resolve_dependencies(test_id)
                    for tid in execution_order:
                        if tid not in all_execution_order:
                            all_execution_order.append(tid)
                except ValueError as e:
                    logger.error(f"Error resolving dependencies for {test_id}: {e}")
        
        # Group tests by dependency level
        test_groups = self._group_tests_by_dependency_level(all_execution_order)
        
        # Run tests in parallel by group
        for group in test_groups:
            if not group:
                continue
            
            # Filter out tests with failed dependencies
            executable_tests = []
            skipped_tests = []
            
            for tid in group:
                if tid not in self.executed_tests:
                    test_case = self.test_cases[tid]
                    dependency_failed = any(dep in self.failed_tests for dep in test_case.dependencies)
                    if dependency_failed:
                        skipped_tests.append(tid)
                    else:
                        executable_tests.append(tid)
            
            # Run executable tests in parallel
            if executable_tests:
                logger.info(f"Running test group: {[self.test_cases[tid].name for tid in executable_tests]}")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_test = {
                        executor.submit(self.run_test_case, self.test_cases[tid]): tid 
                        for tid in executable_tests
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_test):
                        test_id = future_to_test[future]
                        try:
                            result = future.result()
                            results.append(result)
                            self.executed_tests.add(test_id)
                            if not result.success:
                                self.failed_tests.add(test_id)
                            self.save_test_result(result)
                        except Exception as e:
                            error_msg = f"Error running test {test_id}: {str(e)}"
                            logger.error(error_msg)
                            test_case = self.test_cases[test_id]
                            result = TestResult(
                                test_id=test_id,
                                test_name=test_case.name,
                                success=False,
                                message=error_msg,
                                duration=0,
                                error=error_msg
                            )
                            results.append(result)
                            self.executed_tests.add(test_id)
                            self.failed_tests.add(test_id)
                            self.save_test_result(result)
            
            # Handle skipped tests
            for tid in skipped_tests:
                test_case = self.test_cases[tid]
                logger.warning(f"Skipping test {test_case.name} due to failed dependencies", tid)
                result = TestResult(
                    test_id=tid,
                    test_name=test_case.name,
                    success=False,
                    message="Skipped due to failed dependencies",
                    duration=0,
                    error="Dependency failure",
                    logs=[f"Skipped due to failed dependencies: {test_case.dependencies}"]
                )
                results.append(result)
                self.executed_tests.add(tid)
                self.failed_tests.add(tid)
                self.save_test_result(result)
        
        return results
    
    def _group_tests_by_dependency_level(self, execution_order: List[str]) -> List[List[str]]:
        """
        Group tests by dependency level for parallel execution
        
        Args:
            execution_order: List of test IDs in topological order
            
        Returns:
            List of test groups where each group can be executed in parallel
        """
        levels = {}
        for test_id in execution_order:
            max_level = 0
            for dep_id in self.test_cases[test_id].dependencies:
                if dep_id in levels:
                    max_level = max(max_level, levels[dep_id] + 1)
            levels[test_id] = max_level
        
        # Group tests by level
        groups = {}
        for test_id, level in levels.items():
            if level not in groups:
                groups[level] = []
            groups[level].append(test_id)
        
        # Return groups in order
        return [groups[level] for level in sorted(groups.keys())]
    
    def run_tests_by_tags(self, tags: List[str]) -> List[TestResult]:
        """
        Run test cases by tags
        
        Args:
            tags: List of tags
            
        Returns:
            List of TestResult instances
        """
        results = []
        for test_id, test_case in self.test_cases.items():
            if any(tag in test_case.tags for tag in tags):
                results.extend(self.run_test_with_dependencies(test_id))
        return results
    
    def save_test_result(self, result: TestResult):
        """
        Save test result to file
        
        Args:
            result: TestResult instance
        """
        try:
            file_path = os.path.join(self.results_dir, f"{result.test_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Test result saved: {file_path}", result.test_id)
        except Exception as e:
            logger.error(f"Error saving test result: {str(e)}")
    
    def get_test_results(self) -> List[TestResult]:
        """
        Get all test results
        
        Returns:
            List of TestResult instances
        """
        results = []
        
        try:
            for file in os.listdir(self.results_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.results_dir, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Create TestResult from dictionary
                    result = TestResult.from_dict(data)
                    results.append(result)
            
            logger.info(f"Found {len(results)} test results")
            return results
        except Exception as e:
            logger.error(f"Error getting test results: {str(e)}")
            return []
    
    def generate_summary(self, results: List[TestResult]) -> Dict[str, Any]:
        """
        Generate summary statistics
        
        Args:
            results: List of TestResult instances
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "total_duration": 0,
                "timestamp": time.time()
            }
        
        total_tests = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total_tests - passed
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        total_duration = sum(r.duration for r in results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "total_duration": total_duration,
            "timestamp": time.time()
        }
