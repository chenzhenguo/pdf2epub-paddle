# PDF2EPUB Paddle 测试框架使用文档

## 1. 测试框架概述

PDF2EPUB Paddle 项目使用 **pytest** 作为测试框架，提供了一套完整的测试体系，用于验证项目各个功能模块的正确性。测试框架不仅包含了对核心功能的单元测试，还提供了测试报告生成功能，支持 JSON 和 HTML 格式的测试报告。

### 测试框架特点

- **全面的测试覆盖**：覆盖了项目的主要功能模块
- **自动化测试**：支持通过 pytest 自动执行所有测试用例
- **测试报告生成**：自动生成 JSON 和 HTML 格式的测试报告
- **Mock 模拟**：使用 unittest.mock 模拟外部依赖，确保测试的独立性
- **临时文件管理**：使用 tempfile 模块管理测试过程中的临时文件

## 2. 测试环境搭建

### 2.1 安装依赖

测试框架依赖于 pytest，需要先安装开发依赖：

```bash
# 安装开发依赖
pip install -e "[dev]"
```

### 2.2 测试目录结构

测试文件位于 `tests/` 目录下，结构如下：

```
tests/
├── __init__.py            # 初始化文件
├── generate_report.py     # 报告生成脚本
├── report_generator.py    # 测试报告生成器
├── test_pdf2epub_paddle.py # 主要测试文件
├── test_pdf_download.py   # PDF 下载测试
├── test_report_generator.py # 报告生成器测试
└── reports/               # 测试报告输出目录
    ├── test_report.html   # HTML 格式报告
    └── test_report.json   # JSON 格式报告
```

## 3. 测试流程

### 3.1 运行测试

在项目根目录执行以下命令运行测试：

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_pdf2epub_paddle.py

# 运行指定测试函数
pytest tests/test_pdf2epub_paddle.py::test_check_dependencies

# 运行测试并显示详细信息
pytest -v
```

### 3.2 测试执行流程

1. **测试初始化**：创建 `TestReportGenerator` 实例，用于收集测试结果
2. **执行测试用例**：按照测试文件中的顺序执行各个测试函数
3. **收集测试结果**：每个测试用例执行完成后，将结果添加到报告生成器
4. **生成测试报告**：测试全部完成后，生成 JSON 和 HTML 格式的测试报告

### 3.3 测试报告生成

测试完成后，测试报告会自动生成在 `tests/reports/` 目录下：

- **JSON 格式报告**：`tests/reports/test_report.json`，包含详细的测试结果数据
- **HTML 格式报告**：`tests/reports/test_report.html`，提供可视化的测试结果展示

## 4. 测试用例结构

### 4.1 测试用例基本结构

每个测试用例遵循以下结构：

```python
def test_function_name():
    """测试功能描述"""
    start_time = time.time()
    try:
        # 测试代码
        # 断言验证
        duration = time.time() - start_time
        report_generator.add_result("test_function_name", "passed", duration, details=result)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_function_name", "failed", duration, str(e))
        raise
```

### 4.2 测试用例分类

测试用例按照功能模块分类，主要包括：

| 测试类别 | 测试函数 | 功能描述 |
|---------|---------|--------|
| 依赖检查 | `test_check_dependencies` | 验证项目依赖是否正确安装 |
| PDF验证 | `test_validate_pdf_valid` | 验证有效的PDF文件 |
| | `test_validate_pdf_invalid` | 验证无效的PDF文件 |
| | `test_validate_pdf_nonexistent` | 验证不存在的PDF文件 |
| PDF分割 | `test_split_pdf` | 测试PDF文件分割功能 |
| 布局处理 | `test_process_layout_results` | 测试布局结果处理功能 |
| 封面提取 | `test_extract_cover_image` | 测试封面图片提取功能 |
| 标题处理 | `test_extract_candidate_headings` | 测试候选标题提取功能 |
| | `test_filter_heading_candidates` | 测试标题候选过滤功能 |
| 下载功能 | `test_download_image` | 测试图片下载功能 |
| | `test_download_pdf` | 测试PDF下载功能 |
| | `test_download_pdf_invalid_url` | 测试下载无效URL的PDF |
| | `test_download_pdf_non_pdf` | 测试下载非PDF文件 |
| EPUB创建 | `test_create_epub` | 测试EPUB创建功能 |
| API调用 | `test_parse_pdf_chunk` | 测试PDF块解析功能 |
| | `test_parse_pdf_chunk_api_error` | 测试API错误情况 |
| | `test_parse_pdf_chunk_network_error` | 测试网络错误情况 |

## 5. 测试报告生成

### 5.1 报告生成器

测试报告由 `TestReportGenerator` 类生成，支持两种格式：

- **JSON 格式**：包含详细的测试结果数据，便于后续处理和分析
- **HTML 格式**：提供可视化的测试结果展示，便于查看和理解

### 5.2 报告内容

#### JSON 格式报告

```json
{
  "summary": {
    "total_tests": 18,
    "passed": 18,
    "failed": 0,
    "error": 0,
    "start_time": "2023-10-01T12:00:00",
    "end_time": "2023-10-01T12:00:10",
    "duration": 10.0
  },
  "results": [
    {
      "test_name": "test_check_dependencies",
      "status": "passed",
      "duration": 0.1,
      "error_message": null,
      "details": null,
      "timestamp": "2023-10-01T12:00:00"
    }
    // 其他测试结果...
  ]
}
```

#### HTML 格式报告

HTML 格式报告提供了直观的可视化展示，包括：

- 测试摘要：总测试数、通过数、失败数、错误数、总耗时
- 测试结果详情：每个测试用例的执行情况、执行时间、错误信息（如果有）
- 测试元数据：测试开始时间、结束时间、总执行时间

## 6. 示例代码

### 6.1 编写新测试用例

以下是编写新测试用例的示例：

```python
def test_new_function():
    """测试新功能"""
    start_time = time.time()
    try:
        # 测试代码
        result = new_function()
        # 断言验证
        assert result is True
        duration = time.time() - start_time
        report_generator.add_result("test_new_function", "passed", duration, details=result)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_new_function", "failed", duration, str(e))
        raise
```

### 6.2 使用 Mock 模拟外部依赖

```python
@patch('pdf2epub_paddle.requests.get')
def test_function_with_mock(mock_get):
    """测试带有外部依赖的功能"""
    start_time = time.time()
    try:
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_get.return_value = mock_response
        
        # 测试代码
        result = function_under_test()
        # 断言验证
        assert result is True
        duration = time.time() - start_time
        report_generator.add_result("test_function_with_mock", "passed", duration, details=result)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_function_with_mock", "failed", duration, str(e))
        raise
```

### 6.3 使用临时文件

```python
def test_function_with_temp_file():
    """测试需要文件操作的功能"""
    start_time = time.time()
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4\n%e2e3cfd3\n")
            temp_file_path = temp_file.name
        
        try:
            # 测试代码
            result = function_under_test(temp_file_path)
            # 断言验证
            assert result is True
            duration = time.time() - start_time
            report_generator.add_result("test_function_with_temp_file", "passed", duration, details=result)
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_function_with_temp_file", "failed", duration, str(e))
        raise
```

## 7. 最佳实践

### 7.1 测试编写原则

1. **单一职责**：每个测试用例只测试一个功能点
2. **独立性**：测试用例之间相互独立，不依赖于其他测试的执行结果
3. **可重复性**：测试用例可以重复执行，结果一致
4. **全面性**：覆盖正常情况、边界情况和异常情况
5. **清晰性**：测试代码清晰易读，注释充分

### 7.2 测试执行建议

1. **定期执行测试**：在代码变更后及时执行测试，确保功能正常
2. **集成到 CI/CD**：将测试集成到持续集成/持续部署流程中
3. **分析测试报告**：定期分析测试报告，识别潜在问题
4. **优化测试性能**：对于耗时较长的测试，考虑使用并行执行或优化测试逻辑

### 7.3 常见问题处理

1. **测试失败**：检查失败原因，修复代码后重新执行测试
2. **测试超时**：检查测试逻辑，优化测试代码或增加超时时间
3. **依赖问题**：确保测试环境的依赖与生产环境一致
4. **Mock 不当**：确保 Mock 对象的行为与实际对象一致，避免过度模拟

## 8. 总结

PDF2EPUB Paddle 测试框架提供了一套完整的测试体系，通过 pytest 和自定义的报告生成器，实现了对项目功能的全面测试和可视化报告生成。遵循本文档的指导，可以有效地编写和执行测试用例，确保项目的质量和稳定性。

测试框架不仅是保证代码质量的重要工具，也是项目文档的重要组成部分，通过测试用例可以了解项目的功能和使用方式。因此，建议在开发过程中持续完善测试用例，确保测试覆盖率和测试质量。