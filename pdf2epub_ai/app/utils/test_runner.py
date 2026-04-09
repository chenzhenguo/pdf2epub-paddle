import os
import time
import json
from typing import List, Dict, Any, Optional
from app.utils.test_case_manager import TestCaseManager
from app.utils.pdf_downloader import PDFDownloader
from app.utils.pdf_processor import process_pdf
from app.utils.logger import logger


class TestResult:
    """
    Test result class
    """
    def __init__(self, test_id: str, test_name: str, success: bool, 
                 message: str, duration: float, output_path: Optional[str] = None,
                 error: Optional[str] = None):
        """
        Initialize test result
        
        Args:
            test_id: Test case ID
            test_name: Test case name
            success: Whether test passed
            message: Test message
            duration: Test duration in seconds
            output_path: Path to generated EPUB
            error: Error message if test failed
        """
        self.test_id = test_id
        self.test_name = test_name
        self.success = success
        self.message = message
        self.duration = duration
        self.output_path = output_path
        self.error = error
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert test result to dictionary
        
        Returns:
            Dictionary representation of test result
        """
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "success": self.success,
            "message": self.message,
            "duration": self.duration,
            "output_path": self.output_path,
            "error": self.error,
            "timestamp": self.timestamp
        }


class TestRunner:
    """
    Test runner class
    """
    def __init__(self, output_dir: str = "./test_output"):
        """
        Initialize test runner
        
        Args:
            output_dir: Directory to store test results and output files
        """
        self.output_dir = output_dir
        self.results_dir = os.path.join(output_dir, "results")
        self.epub_dir = os.path.join(output_dir, "epub")
        
        # Create directories
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.epub_dir, exist_ok=True)
        
        self.test_case_manager = TestCaseManager()
        self.pdf_downloader = PDFDownloader()
    
    def run_test_case(self, test_case) -> TestResult:
        """
        Run a single test case
        
        Args:
            test_case: TestCase instance
            
        Returns:
            TestResult instance
        """
        start_time = time.time()
        
        try:
            logger.info(f"Running test case: {test_case.name}")
            
            # Handle online PDF sources
            if test_case.is_online:
                logger.info(f"Downloading online PDF: {test_case.pdf_source}")
                pdf_path = self.pdf_downloader.download(test_case.pdf_source)
                if not pdf_path:
                    error_msg = f"Failed to download PDF from {test_case.pdf_source}"
                    logger.error(error_msg)
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        success=False,
                        message=error_msg,
                        duration=time.time() - start_time,
                        error=error_msg
                    )
            else:
                # Use local PDF file
                pdf_path = test_case.pdf_source
                if not os.path.exists(pdf_path):
                    error_msg = f"Local PDF file not found: {pdf_path}"
                    logger.error(error_msg)
                    return TestResult(
                        test_id=test_case.test_id,
                        test_name=test_case.name,
                        success=False,
                        message=error_msg,
                        duration=time.time() - start_time,
                        error=error_msg
                    )
            
            # Generate output path
            output_filename = f"{test_case.test_id}.epub"
            output_path = os.path.join(self.epub_dir, output_filename)
            
            # Process PDF
            logger.info(f"Processing PDF: {pdf_path}")
            success, message = process_pdf(
                pdf_path,
                output_path,
                title=test_case.expected_title,
                author=test_case.expected_author
            )
            
            duration = time.time() - start_time
            
            if success:
                logger.info(f"Test passed: {test_case.name}")
                return TestResult(
                    test_id=test_case.test_id,
                    test_name=test_case.name,
                    success=True,
                    message=message,
                    duration=duration,
                    output_path=output_path
                )
            else:
                logger.error(f"Test failed: {test_case.name} - {message}")
                return TestResult(
                    test_id=test_case.test_id,
                    test_name=test_case.name,
                    success=False,
                    message=message,
                    duration=duration,
                    error=message
                )
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return TestResult(
                test_id=test_case.test_id,
                test_name=test_case.name,
                success=False,
                message=error_msg,
                duration=time.time() - start_time,
                error=error_msg
            )
    
    def run_test_cases(self, test_cases: List) -> List[TestResult]:
        """
        Run multiple test cases
        
        Args:
            test_cases: List of TestCase instances
            
        Returns:
            List of TestResult instances
        """
        results = []
        
        for test_case in test_cases:
            result = self.run_test_case(test_case)
            results.append(result)
            
            # Save result
            self.save_test_result(result)
        
        return results
    
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all test cases
        
        Returns:
            List of TestResult instances
        """
        test_cases = self.test_case_manager.list_test_cases()
        return self.run_test_cases(test_cases)
    
    def run_tests_by_tags(self, tags: List[str]) -> List[TestResult]:
        """
        Run test cases by tags
        
        Args:
            tags: List of tags
            
        Returns:
            List of TestResult instances
        """
        test_cases = self.test_case_manager.get_test_case_by_tags(tags)
        return self.run_test_cases(test_cases)
    
    def run_online_tests(self) -> List[TestResult]:
        """
        Run online test cases
        
        Returns:
            List of TestResult instances
        """
        test_cases = self.test_case_manager.get_online_test_cases()
        return self.run_test_cases(test_cases)
    
    def run_local_tests(self) -> List[TestResult]:
        """
        Run local test cases
        
        Returns:
            List of TestResult instances
        """
        test_cases = self.test_case_manager.get_local_test_cases()
        return self.run_test_cases(test_cases)
    
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
            logger.info(f"Test result saved: {file_path}")
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
                    result = TestResult(
                        test_id=data.get("test_id"),
                        test_name=data.get("test_name"),
                        success=data.get("success"),
                        message=data.get("message"),
                        duration=data.get("duration"),
                        output_path=data.get("output_path"),
                        error=data.get("error")
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} test results")
            return results
        except Exception as e:
            logger.error(f"Error getting test results: {str(e)}")
            return []
