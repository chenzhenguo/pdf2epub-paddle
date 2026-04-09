import os
import json
import csv
import time
from typing import List, Dict, Any
from datetime import datetime

from .test_result import TestResult
from .logger import logger


class TestReporter:
    """
    Enhanced test reporting system
    """
    def __init__(self, output_dir: str = "./test_reports"):
        """
        Initialize test reporter
        
        Args:
            output_dir: Directory to store test reports
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
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
        
        # Generate CSV report
        csv_path = os.path.join(self.output_dir, f"{report_name}.csv")
        self._generate_csv_report(results, csv_path)
        report_paths["csv"] = csv_path
        
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
            
            # Add detailed information for each test
            for result in results:
                detailed_info = {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "success": result.success,
                    "duration": result.duration,
                    "message": result.message,
                    "error": result.error,
                    "output": result.output,
                    "logs": result.logs,
                    "start_time": result.start_time,
                    "timestamp": result.timestamp
                }
                report_data["detailed_results"].append(detailed_info)
            
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
                <title>Enhanced Test Execution Report</title>
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
                    .test-logs {{
                        margin-top: 10px;
                        padding: 10px;
                        background-color: #f9f9f9;
                        border-radius: 3px;
                        font-family: monospace;
                        font-size: 12px;
                        max-height: 200px;
                        overflow-y: auto;
                    }}
                    .test-logs h4 {{
                        margin-top: 0;
                        font-size: 12px;
                        color: #666;
                    }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .test-output {{
                        margin-top: 10px;
                        padding: 10px;
                        background-color: #f0f8ff;
                        border-radius: 3px;
                        font-family: monospace;
                        font-size: 12px;
                        max-height: 100px;
                        overflow-y: auto;
                    }}
                    .test-output h4 {{
                        margin-top: 0;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <h1>Enhanced Test Execution Report</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <div class="summary-item"><span class="summary-label">Total Tests:</span> {summary['total_tests']}</div>
                    <div class="summary-item"><span class="summary-label">Passed:</span> {summary['passed']}</div>
                    <div class="summary-item"><span class="summary-label">Failed:</span> {summary['failed']}</div>
                    <div class="summary-item"><span class="summary-label">Success Rate:</span> {summary['success_rate']:.2f}%</div>
                    <div class="summary-item"><span class="summary-label">Average Duration:</span> {summary['avg_duration']:.2f}s</div>
                    <div class="summary-item"><span class="summary-label">Total Duration:</span> {summary['total_duration']:.2f}s</div>
                    <div class="summary-item"><span class="summary-label">Min Duration:</span> {summary['min_duration']:.2f}s</div>
                    <div class="summary-item"><span class="summary-label">Max Duration:</span> {summary['max_duration']:.2f}s</div>
                    <div class="summary-item"><span class="summary-label">Duration Std Dev:</span> {summary['duration_std_dev']:.2f}s</div>
                </div>
            '''
            
            # Add error distribution if available
            if summary['error_distribution']:
                html_content += f'''
                <div class="summary">
                    <h2>Error Distribution</h2>
                    <table>
                        <tr>
                            <th>Error Type</th>
                            <th>Count</th>
                        </tr>
                '''
                for error_type, count in summary['error_distribution'].items():
                    html_content += f'''
                        <tr>
                            <td>{error_type}</td>
                            <td>{count}</td>
                        </tr>
                    '''
                html_content += f'''
                    </table>
                </div>
                '''
            
            html_content += f'''
                <div class="test-results">
                    <h2>Test Results</h2>
            '''
            
            # Add test cases
            for result in results:
                status_class = "success" if result.success else "failure"
                status_text = "PASSED" if result.success else "FAILED"
                status_color = "status-success" if result.success else "status-failure"
                
                error_html = f"<div class='test-error'><strong>Error:</strong> {result.error}</div>" if result.error else ""
                
                # Format output if it's a dictionary or list
                output_html = ""
                if result.output:
                    if isinstance(result.output, (dict, list)):
                        output_str = json.dumps(result.output, indent=2)
                    else:
                        output_str = str(result.output)
                    output_html = f"<div class='test-output'><h4>Output:</h4><pre>{output_str}</pre></div>"
                
                # Add logs
                logs_html = ""
                if result.logs:
                    logs_str = "\n".join(result.logs)
                    logs_html = f"<div class='test-logs'><h4>Logs:</h4><pre>{logs_str}</pre></div>"
                
                # Format timestamps
                start_time_str = datetime.fromtimestamp(result.start_time).strftime("%Y-%m-%d %H:%M:%S")
                end_time_str = datetime.fromtimestamp(result.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
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
                            <strong>Test ID:</strong> {result.test_id}<br>
                            <strong>Start Time:</strong> {start_time_str}<br>
                            <strong>End Time:</strong> {end_time_str}<br>
                            {error_html}
                            {output_html}
                            {logs_html}
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
                "total_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "duration_std_dev": 0,
                "error_distribution": {}
            }
        
        total_tests = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total_tests - passed
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        # Duration metrics
        durations = [r.duration for r in results]
        total_duration = sum(durations)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Calculate standard deviation of durations
        if total_tests > 1:
            mean = avg_duration
            variance = sum((d - mean) ** 2 for d in durations) / (total_tests - 1)
            duration_std_dev = variance ** 0.5
        else:
            duration_std_dev = 0
        
        # Error distribution
        error_distribution = {}
        for result in results:
            if not result.success and result.error:
                # Extract error type from error message
                error_type = result.error.split(':')[0] if ':' in result.error else 'Unknown'
                error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "total_duration": total_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "duration_std_dev": duration_std_dev,
            "error_distribution": error_distribution
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
    
    def _generate_csv_report(self, results: List[TestResult], output_path: str):
        """
        Generate CSV report
        
        Args:
            results: List of TestResult instances
            output_path: Path to output CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                writer.writerow([
                    'Test ID', 'Test Name', 'Success', 'Message', 'Duration (s)',
                    'Error', 'Output', 'Start Time', 'End Time'
                ])
                
                # Write test results
                for result in results:
                    # Format timestamps
                    start_time_str = datetime.fromtimestamp(result.start_time).strftime("%Y-%m-%d %H:%M:%S")
                    end_time_str = datetime.fromtimestamp(result.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Format output if it's a dictionary or list
                    output_str = ''
                    if result.output:
                        if isinstance(result.output, (dict, list)):
                            output_str = json.dumps(result.output, indent=0)
                        else:
                            output_str = str(result.output)
                    
                    # Write row
                    writer.writerow([
                        result.test_id,
                        result.test_name,
                        'PASS' if result.success else 'FAIL',
                        result.message,
                        f"{result.duration:.2f}",
                        result.error or '',
                        output_str,
                        start_time_str,
                        end_time_str
                    ])
            
            logger.info(f"CSV report generated: {output_path}")
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
    
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
                    result = TestResult.from_dict(data)
                    results.append(result)
            
            logger.info(f"Loaded {len(results)} test results from {results_dir}")
            return results
        except Exception as e:
            logger.error(f"Error loading test results: {str(e)}")
            return []
    
    def analyze_trends(self, test_runs: List[List[TestResult]]) -> Dict[str, Any]:
        """
        Analyze trends across multiple test runs
        
        Args:
            test_runs: List of test runs, each containing a list of TestResult instances
            
        Returns:
            Dictionary with trend analysis results
        """
        if not test_runs:
            return {}
        
        try:
            trend_data = {
                "runs_analyzed": len(test_runs),
                "success_rates": [],
                "avg_durations": [],
                "total_tests": [],
                "passed_tests": [],
                "failed_tests": [],
                "trends": {}
            }
            
            # Analyze each test run
            for i, run in enumerate(test_runs):
                summary = self._generate_summary(run)
                trend_data["success_rates"].append(summary["success_rate"])
                trend_data["avg_durations"].append(summary["avg_duration"])
                trend_data["total_tests"].append(summary["total_tests"])
                trend_data["passed_tests"].append(summary["passed"])
                trend_data["failed_tests"].append(summary["failed"])
            
            # Calculate trends
            if len(test_runs) > 1:
                # Success rate trend
                success_rate_change = trend_data["success_rates"][-1] - trend_data["success_rates"][0]
                trend_data["trends"]["success_rate"] = {
                    "change": success_rate_change,
                    "direction": "improving" if success_rate_change > 0 else "declining" if success_rate_change < 0 else "stable"
                }
                
                # Duration trend
                duration_change = trend_data["avg_durations"][-1] - trend_data["avg_durations"][0]
                trend_data["trends"]["duration"] = {
                    "change": duration_change,
                    "direction": "improving" if duration_change < 0 else "declining" if duration_change > 0 else "stable"
                }
            
            return trend_data
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}
    
    def compare_runs(self, run1: List[TestResult], run2: List[TestResult]) -> Dict[str, Any]:
        """
        Compare two test runs
        
        Args:
            run1: First test run (baseline)
            run2: Second test run (comparison)
            
        Returns:
            Dictionary with comparison results
        """
        try:
            summary1 = self._generate_summary(run1)
            summary2 = self._generate_summary(run2)
            
            comparison = {
                "baseline": summary1,
                "comparison": summary2,
                "changes": {
                    "success_rate": summary2["success_rate"] - summary1["success_rate"],
                    "avg_duration": summary2["avg_duration"] - summary1["avg_duration"],
                    "total_tests": summary2["total_tests"] - summary1["total_tests"],
                    "passed_tests": summary2["passed"] - summary1["passed"],
                    "failed_tests": summary2["failed"] - summary1["failed"]
                }
            }
            
            # Identify new failures and improvements
            run1_test_ids = {r.test_id: r for r in run1}
            run2_test_ids = {r.test_id: r for r in run2}
            
            new_failures = []
            improvements = []
            
            for test_id, test in run2_test_ids.items():
                if test_id in run1_test_ids:
                    # Test existed in both runs
                    if not test.success and run1_test_ids[test_id].success:
                        new_failures.append(test.test_name)
                    elif test.success and not run1_test_ids[test_id].success:
                        improvements.append(test.test_name)
                else:
                    # New test
                    if not test.success:
                        new_failures.append(test.test_name)
            
            comparison["new_failures"] = new_failures
            comparison["improvements"] = improvements
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing runs: {str(e)}")
            return {}
