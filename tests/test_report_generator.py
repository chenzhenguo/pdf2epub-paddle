import os
import sys
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_generator import TestReportGenerator

# 测试报告生成器
def test_report_generator():
    """测试报告生成器功能"""
    # 创建报告生成器
    generator = TestReportGenerator()
    
    # 添加测试结果
    generator.add_result("test1", "passed", 0.1)
    generator.add_result("test2", "failed", 0.2, "Error message")
    generator.add_result("test3", "error", 0.3, "Exception occurred")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 生成JSON报告
        json_path = os.path.join(temp_dir, "report.json")
        json_result = generator.generate_report(json_path, "json")
        assert os.path.exists(json_result)
        print(f"JSON报告生成成功: {json_result}")
        
        # 生成HTML报告
        html_path = os.path.join(temp_dir, "report.html")
        html_result = generator.generate_report(html_path, "html")
        assert os.path.exists(html_result)
        print(f"HTML报告生成成功: {html_result}")

if __name__ == "__main__":
    test_report_generator()