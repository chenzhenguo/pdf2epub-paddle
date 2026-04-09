import json
import os
from datetime import datetime
from typing import List, Dict, Any

class TestReportGenerator:
    """
    测试报告生成器，支持HTML和JSON格式输出
    """
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_result(self, test_name: str, status: str, duration: float, error_message: str = None, details: Dict = None):
        """
        添加测试结果
        
        Args:
            test_name: 测试名称
            status: 测试状态 ("passed", "failed", "error")
            duration: 测试执行时间（秒）
            error_message: 错误信息（如果有）
            details: 测试详细信息（如果有）
        """
        result = {
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error_message": error_message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
    
    def generate_json_report(self, output_path: str) -> str:
        """
        生成JSON格式的测试报告
        
        Args:
            output_path: 输出文件路径
        
        Returns:
            生成的报告文件路径
        """
        self.end_time = datetime.now()
        report = {
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["status"] == "passed"),
                "failed": sum(1 for r in self.test_results if r["status"] == "failed"),
                "error": sum(1 for r in self.test_results if r["status"] == "error"),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration": (self.end_time - self.start_time).total_seconds()
            },
            "results": self.test_results
        }
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def generate_html_report(self, output_path: str) -> str:
        """
        生成HTML格式的测试报告
        
        Args:
            output_path: 输出文件路径
        
        Returns:
            生成的报告文件路径
        """
        self.end_time = datetime.now()
        
        # 计算统计信息
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "passed")
        failed = sum(1 for r in self.test_results if r["status"] == "failed")
        error = sum(1 for r in self.test_results if r["status"] == "error")
        duration = (self.end_time - self.start_time).total_seconds()
        
        # 生成HTML内容
        html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .summary {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
        .summary-item {
            text-align: center;
        }
        .summary-item .count {
            font-size: 24px;
            font-weight: bold;
        }
        .summary-item .label {
            font-size: 14px;
            color: #666;
        }
        .passed {
            color: #4CAF50;
        }
        .failed {
            color: #f44336;
        }
        .error {
            color: #ff9800;
        }
        .test-results {
            margin-top: 30px;
        }
        .test-case {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .test-case.passed {
            border-left: 5px solid #4CAF50;
        }
        .test-case.failed {
            border-left: 5px solid #f44336;
        }
        .test-case.error {
            border-left: 5px solid #ff9800;
        }
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .test-name {
            font-weight: bold;
            font-size: 16px;
        }
        .test-status {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .test-status.passed {
            background-color: #e8f5e8;
        }
        .test-status.failed {
            background-color: #ffebee;
        }
        .test-status.error {
            background-color: #fff3e0;
        }
        .test-details {
            margin-top: 10px;
            font-size: 14px;
        }
        .error-message {
            background-color: #ffebee;
            padding: 10px;
            border-radius: 3px;
            margin-top: 10px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .metadata {
            margin-top: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF2EPUB Paddle 测试报告</h1>
        
        <div class="summary">
            <div class="summary-item">
                <div class="count">'''
        html_content += f"{total_tests}"
        html_content += '''</div>
                <div class="label">总测试数</div>
            </div>
            <div class="summary-item">
                <div class="count passed">'''
        html_content += f"{passed}"
        html_content += '''</div>
                <div class="label">通过</div>
            </div>
            <div class="summary-item">
                <div class="count failed">'''
        html_content += f"{failed}"
        html_content += '''</div>
                <div class="label">失败</div>
            </div>
            <div class="summary-item">
                <div class="count error">'''
        html_content += f"{error}"
        html_content += '''</div>
                <div class="label">错误</div>
            </div>
            <div class="summary-item">
                <div class="count">'''
        html_content += f"{duration:.2f}s"
        html_content += '''</div>
                <div class="label">总耗时</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>测试结果详情</h2>
        '''
        
        # 添加测试用例详情
        for result in self.test_results:
            status_class = result["status"]
            status_text = "通过" if status_class == "passed" else "失败" if status_class == "failed" else "错误"
            
            test_case_html = f"""
            <div class="test-case {status_class}">
                <div class="test-header">
                    <div class="test-name">{result['test_name']}</div>
                    <div class="test-status {status_class}">{status_text}</div>
                </div>
                <div class="test-details">
                    <p>执行时间: {result['duration']:.3f} 秒</p>
                    <p>执行时间: {result['timestamp']}</p>
                </div>
            """
            
            if result['error_message']:
                test_case_html += f"""
                <div class="error-message">
                    错误信息:
                    <pre>{result['error_message']}</pre>
                </div>
                """
            
            if result['details']:
                test_case_html += f"""
                <div class="test-details">
                    <p>详细信息:</p>
                    <pre>{json.dumps(result['details'], indent=2, ensure_ascii=False)}</pre>
                </div>
                """
            
            test_case_html += "</div>"
            html_content += test_case_html
        
        # 添加元数据
        html_content += f"""
        </div>
        
        <div class="metadata">
            <h3>测试元数据</h3>
            <p>开始时间: {self.start_time.isoformat()}</p>
            <p>结束时间: {self.end_time.isoformat()}</p>
            <p>总执行时间: {duration:.2f} 秒</p>
        </div>
    </div>
</body>
</html>
        """
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path
    
    def generate_report(self, output_path: str, format: str = "json") -> str:
        """
        生成测试报告
        
        Args:
            output_path: 输出文件路径
            format: 报告格式 ("json" 或 "html")
        
        Returns:
            生成的报告文件路径
        """
        if format.lower() == "json":
            return self.generate_json_report(output_path)
        elif format.lower() == "html":
            return self.generate_html_report(output_path)
        else:
            raise ValueError(f"不支持的报告格式: {format}")
