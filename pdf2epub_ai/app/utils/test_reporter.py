import os
import json
import time
from typing import List, Dict, Any
from app.utils.test_runner import TestResult
from app.utils.epub_validator import EPUBValidator
from app.utils.logger import logger


class TestReporter:
    """
    Test reporting system
    """
    def __init__(self, output_dir: str = "./test_reports"):
        """
        Initialize test reporter
        
        Args:
            output_dir: Directory to store test reports
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.epub_validator = EPUBValidator()
    
    def generate_report(self, results: List[TestResult], report_name: str = None) -> Dict[str, str]:
        """
        Generate test report in multiple formats
        
        Args:
            results: List of TestResult instances
            report_name: Custom report name
            
        Returns:
            Dictionary with paths to generated reports
        """
        if not report_name:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_name = f"test_report_{timestamp}"
        
        report_paths = {}
        
        # Generate JSON report
        json_path = os.path.join(self.output_dir, f"{report_name}.json")
        self._generate_json_report(results, json_path)
        report_paths["json"] = json_path
        
        # Generate HTML report
        html_path = os.path.join(self.output_dir, f"{report_name}.html")
        self._generate_html_report(results, html_path)
        report_paths["html"] = html_path
        
        logger.info(f"Test reports generated: {report_paths}")
        return report_paths
    
    def _generate_json_report(self, results: List[TestResult], output_path: str):
        """
        Generate JSON report
        
        Args:
            results: List of TestResult instances
            output_path: Path to output JSON file
        """
        try:
            report_data = {
                "timestamp": time.time(),
                "summary": self._generate_summary(results),
                "results": [result.to_dict() for result in results],
                "detailed_results": []
            }
            
            # Add detailed validation results for successful tests
            for result in results:
                if result.success and result.output_path:
                    epub_info = self.epub_validator.get_epub_info(result.output_path)
                    if epub_info:
                        report_data["detailed_results"].append({
                            "test_id": result.test_id,
                            "test_name": result.test_name,
                            "epub_info": epub_info
                        })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON report generated: {output_path}")
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
    
    def _generate_html_report(self, results: List[TestResult], output_path: str):
        """
        Generate HTML report
        
        Args:
            results: List of TestResult instances
            output_path: Path to output HTML file
        """
        try:
            summary = self._generate_summary(results)
            
            # Generate HTML content
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>PDF to EPUB Test Report</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f5f5f5;
                    }}
                    h1, h2, h3 {{
                        color: #333;
                    }}
                    .summary {{
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    .summary-item {{
                        display: inline-block;
                        margin-right: 30px;
                        margin-bottom: 10px;
                    }}
                    .summary-label {{
                        font-weight: bold;
                        color: #555;
                    }}
                    .test-results {{
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .test-case {{
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        padding: 15px;
                        margin-bottom: 15px;
                    }}
                    .test-case.success {{
                        border-left: 4px solid #4CAF50;
                    }}
                    .test-case.failure {{
                        border-left: 4px solid #f44336;
                    }}
                    .test-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 10px;
                    }}
                    .test-name {{
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    .test-status {{
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 12px;
                        font-weight: bold;
                    }}
                    .status-success {{
                        background-color: #4CAF50;
                        color: white;
                    }}
                    .status-failure {{
                        background-color: #f44336;
                        color: white;
                    }}
                    .test-details {{
                        margin-top: 10px;
                        font-size: 14px;
                    }}
                    .test-error {{
                        color: #f44336;
                        margin-top: 5px;
                    }}
                    .duration {{ color: #666; font-size: 12px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>PDF to EPUB Test Report</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <div class="summary-item"><span class="summary-label">Total Tests:</span> {summary['total_tests']}</div>
                    <div class="summary-item"><span class="summary-label">Passed:</span> {summary['passed']}</div>
                    <div class="summary-item"><span class="summary-label">Failed:</span> {summary['failed']}</div>
                    <div class="summary-item"><span class="summary-label">Success Rate:</span> {summary['success_rate']:.2f}%</div>
                    <div class="summary-item"><span class="summary-label">Average Duration:</span> {summary['avg_duration']:.2f}s</div>
                    <div class="summary-item"><span class="summary-label">Total Duration:</span> {summary['total_duration']:.2f}s</div>
                </div>
                <div class="test-results">
                    <h2>Test Results</h2>
            '''
            
            # Add test cases
            for result in results:
                status_class = "success" if result.success else "failure"
                status_text = "PASSED" if result.success else "FAILED"
                status_color = "status-success" if result.success else "status-failure"
                
                error_html = f"<div class='test-error'><strong>Error:</strong> {result.error}</div>" if result.error else ""
                
                html_content += f"""
                    <div class="test-case {status_class}">
                        <div class="test-header">
                            <div class="test-name">{result.test_name}</div>
                            <div>
                                <span class="test-status {status_color}">{status_text}</span>
                                <span class="duration">({result.duration:.2f}s)</span>
                            </div>
                        </div>
                        <div class="test-details">
                            <strong>Message:</strong> {result.message}<br>
                            {error_html}
                            {f"<strong>Output:</strong> {result.output_path}" if result.output_path else ""}
                        </div>
                    </div>
                """
            
            # Add footer
            html_content += f'''
                </div>
                <p style="margin-top: 20px; font-size: 12px; color: #666;">
                    Report generated on {time.strftime("%Y-%m-%d %H:%M:%S")}
                </p>
            </body>
            </html>
            '''
            
            # No need to replace placeholders as we're using f-strings with dictionary access
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
    
    def _generate_summary(self, results: List[TestResult]) -> Dict[str, Any]:
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
                "total_duration": 0
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
            "total_duration": total_duration
        }
    
    def generate_summary_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """
        Generate summary report
        
        Args:
            results: List of TestResult instances
            
        Returns:
            Dictionary with summary report
        """
        summary = self._generate_summary(results)
        
        # Get detailed failure information
        failures = [r for r in results if not r.success]
        failure_details = [{
            "test_id": r.test_id,
            "test_name": r.test_name,
            "error": r.error,
            "duration": r.duration
        } for r in failures]
        
        return {
            **summary,
            "failures": failure_details,
            "timestamp": time.time()
        }
    
    def load_test_results(self, results_dir: str) -> List[TestResult]:
        """
        Load test results from directory
        
        Args:
            results_dir: Directory containing test result files
            
        Returns:
            List of TestResult instances
        """
        results = []
        
        try:
            for file in os.listdir(results_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(results_dir, file)
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
            
            logger.info(f"Loaded {len(results)} test results from {results_dir}")
            return results
        except Exception as e:
            logger.error(f"Error loading test results: {str(e)}")
            return []
