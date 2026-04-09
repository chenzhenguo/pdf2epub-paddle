import os
import tempfile
import pytest
import json
import time
from unittest.mock import patch, MagicMock
from pdf2epub_paddle import (
    check_dependencies,
    validate_pdf,
    split_pdf,
    parse_pdf_chunk,
    process_layout_results,
    extract_cover_image,
    extract_candidate_headings,
    filter_heading_candidates,
    download_image,
    download_pdf,
    create_epub
)
from .report_generator import TestReportGenerator

# 全局测试报告生成器
report_generator = TestReportGenerator()

# 测试运行完成后生成报告
def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时生成报告"""
    # 生成JSON报告
    json_report_path = os.path.join(os.path.dirname(__file__), "reports", "test_report.json")
    report_generator.generate_report(json_report_path, format="json")
    
    # 生成HTML报告
    html_report_path = os.path.join(os.path.dirname(__file__), "reports", "test_report.html")
    report_generator.generate_report(html_report_path, format="html")
    
    print(f"\n测试报告已生成:")
    print(f"- JSON格式: {json_report_path}")
    print(f"- HTML格式: {html_report_path}")

# 测试依赖检查
def test_check_dependencies():
    """测试依赖项检查功能"""
    start_time = time.time()
    try:
        # 正常情况：所有依赖都已安装
        assert check_dependencies() is True
        duration = time.time() - start_time
        report_generator.add_result("test_check_dependencies", "passed", duration)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_check_dependencies", "failed", duration, str(e))
        raise

# 测试PDF验证
@patch('pdf2epub_paddle.fitz')
def test_validate_pdf_valid(mock_fitz):
    """测试验证有效的PDF文件"""
    start_time = time.time()
    try:
        # 模拟fitz对象
        mock_doc = MagicMock()
        mock_doc.is_closed = False
        mock_doc.metadata = {}
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 验证PDF
            result = validate_pdf(temp_file_path)
            assert result["valid"] is True
            assert "metadata" in result
            assert "page_count" in result["metadata"]
            assert result["metadata"]["page_count"] == 1
            duration = time.time() - start_time
            report_generator.add_result("test_validate_pdf_valid", "passed", duration, details=result)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_validate_pdf_valid", "failed", duration, str(e))
        raise

@patch('pdf2epub_paddle.fitz')
def test_validate_pdf_invalid(mock_fitz):
    """测试验证无效的PDF文件"""
    start_time = time.time()
    try:
        # 模拟fitz.open抛出异常
        mock_fitz.open.side_effect = Exception("Not a PDF file")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is not a PDF file")
            temp_file_path = temp_file.name
        
        try:
            # 验证非PDF文件
            result = validate_pdf(temp_file_path)
            assert result["valid"] is False
            assert "error" in result
            duration = time.time() - start_time
            report_generator.add_result("test_validate_pdf_invalid", "passed", duration, details=result)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_validate_pdf_invalid", "failed", duration, str(e))
        raise

def test_validate_pdf_nonexistent():
    """测试验证不存在的PDF文件"""
    start_time = time.time()
    try:
        # 验证不存在的文件
        result = validate_pdf("nonexistent_file.pdf")
        assert result["valid"] is False
        assert "error" in result
        duration = time.time() - start_time
        report_generator.add_result("test_validate_pdf_nonexistent", "passed", duration, details=result)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_validate_pdf_nonexistent", "failed", duration, str(e))
        raise

# 测试PDF分割
@patch('pdf2epub_paddle.fitz')
def test_split_pdf(mock_fitz):
    """测试PDF分割功能"""
    start_time = time.time()
    try:
        # 模拟fitz对象
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_doc.is_closed = False
        mock_doc.metadata = {}
        
        mock_chunk_doc = MagicMock()
        mock_chunk_doc.insert_pdf = MagicMock()
        mock_chunk_doc.save = MagicMock()
        mock_chunk_doc.close = MagicMock()
        
        mock_fitz.open.side_effect = [mock_doc, mock_chunk_doc, mock_chunk_doc, mock_chunk_doc]
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4\n%e2e3cfd3\n")
            temp_file_path = temp_file.name
        
        try:
            # 分割PDF
            chunks = split_pdf(temp_file_path, chunk_size=1)
            assert len(chunks) == 3
            # 验证fitz.open被调用
            assert mock_fitz.open.called
            duration = time.time() - start_time
            report_generator.add_result("test_split_pdf", "passed", duration, details={"chunk_count": len(chunks)})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_split_pdf", "failed", duration, str(e))
        raise

# 测试布局结果处理
def test_process_layout_results():
    """测试布局结果处理功能"""
    start_time = time.time()
    try:
        test_result = {"result": {"layoutParsingResults": []}}
        result = process_layout_results(test_result, "test_chunk.pdf")
        assert result == test_result
        duration = time.time() - start_time
        report_generator.add_result("test_process_layout_results", "passed", duration)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_process_layout_results", "failed", duration, str(e))
        raise

# 测试封面图片提取
@patch('pdf2epub_paddle.fitz')
def test_extract_cover_image(mock_fitz):
    """测试封面图片提取功能"""
    start_time = time.time()
    try:
        # 模拟fitz对象
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.load_page.return_value = MagicMock()
        mock_doc.close = MagicMock()
        
        mock_page = MagicMock()
        mock_doc.load_page.return_value = mock_page
        
        mock_mat = MagicMock()
        mock_fitz.Matrix.return_value = mock_mat
        
        mock_pix = MagicMock()
        mock_pix.save = MagicMock()
        mock_page.get_pixmap.return_value = mock_pix
        
        mock_fitz.open.return_value = mock_doc
        
        # 创建临时文件路径
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_cover:
            cover_path = temp_cover.name
        
        try:
            # 提取封面图片
            result = extract_cover_image(temp_file_path, cover_path)
            assert result == cover_path
            # 验证fitz.open被调用
            assert mock_fitz.open.called
            # 验证pix.save被调用
            mock_pix.save.assert_called_with(cover_path)
            duration = time.time() - start_time
            report_generator.add_result("test_extract_cover_image", "passed", duration, details={"cover_path": result})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(cover_path):
                os.unlink(cover_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_extract_cover_image", "failed", duration, str(e))
        raise

# 测试候选标题提取
def test_extract_candidate_headings():
    """测试候选标题提取功能"""
    start_time = time.time()
    try:
        # 模拟API结果
        test_results = [
            {
                "result": {
                    "layoutParsingResults": [
                        {
                            "markdown": {
                                "text": "# Chapter 1 Introduction\nSome text\n## Section 1.1 Overview"
                            }
                        }
                    ]
                }
            }
        ]
        
        candidates = extract_candidate_headings(test_results)
        assert len(candidates) == 2
        assert candidates[0]["title"] == "Chapter 1 Introduction"
        assert candidates[0]["level"] == 1
        assert candidates[1]["title"] == "Section 1.1 Overview"
        assert candidates[1]["level"] == 2
        duration = time.time() - start_time
        report_generator.add_result("test_extract_candidate_headings", "passed", duration, details={"candidate_count": len(candidates)})
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_extract_candidate_headings", "failed", duration, str(e))
        raise

# 测试标题候选过滤
def test_filter_heading_candidates():
    """测试标题候选过滤功能"""
    start_time = time.time()
    try:
        # 模拟候选标题
        candidates = [
            {"title": "Chapter 1", "level": 1, "page": 3},
            {"title": "Chapter 2", "level": 1, "page": 10},
            {"title": "Chapter 3", "level": 1, "page": 20},
            {"title": "Chapter 4", "level": 1, "page": 30},
            {"title": "Section 1.1", "level": 2, "page": 4}
        ]
        
        # 测试H1-only策略
        filtered = filter_heading_candidates(candidates)
        assert len(filtered) == 4
        for item in filtered:
            assert item["level"] == 1
        duration = time.time() - start_time
        report_generator.add_result("test_filter_heading_candidates", "passed", duration, details={"filtered_count": len(filtered)})
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_filter_heading_candidates", "failed", duration, str(e))
        raise

# 测试图片下载
@patch('pdf2epub_paddle.requests.get')
def test_download_image(mock_get):
    """测试图片下载功能"""
    start_time = time.time()
    try:
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_get.return_value = mock_response
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 下载图片
            success = download_image("https://example.com/image.png", temp_file_path)
            assert success is True
            assert os.path.exists(temp_file_path)
            assert os.path.getsize(temp_file_path) > 0
            duration = time.time() - start_time
            report_generator.add_result("test_download_image", "passed", duration, details={"success": success})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_download_image", "failed", duration, str(e))
        raise

# 测试PDF下载
@patch('pdf2epub_paddle.requests.get')
@patch('builtins.open', new_callable=MagicMock)
def test_download_pdf(mock_open, mock_get):
    """测试PDF下载功能"""
    start_time = time.time()
    try:
        # 模拟文件对象
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            'content-type': 'application/pdf',
            'content-length': '19'
        }
        # 提供完整的PDF魔术数字
        mock_response.iter_content.return_value = [b"%PDF-1.4\n%e2e3cfd3\n"]
        mock_get.return_value = mock_response
        
        # 模拟文件读取，返回正确的魔术数字
        mock_file.read.side_effect = [b"%PDF-"]
        
        # 创建临时文件路径
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 下载PDF
            success = download_pdf("https://example.com/test.pdf", temp_file_path)
            assert success is True
            duration = time.time() - start_time
            report_generator.add_result("test_download_pdf", "passed", duration, details={"success": success})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_download_pdf", "failed", duration, str(e))
        raise

def test_download_pdf_invalid_url():
    """测试下载无效URL的PDF"""
    start_time = time.time()
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 尝试下载无效URL
            success = download_pdf("https://example.com/nonexistent.pdf", temp_file_path)
            assert success is False
            duration = time.time() - start_time
            report_generator.add_result("test_download_pdf_invalid_url", "passed", duration, details={"success": success})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_download_pdf_invalid_url", "failed", duration, str(e))
        raise

def test_download_pdf_non_pdf():
    """测试下载非PDF文件"""
    start_time = time.time()
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 尝试下载HTML文件作为PDF
            success = download_pdf("https://example.com", temp_file_path)
            assert success is False
            duration = time.time() - start_time
            report_generator.add_result("test_download_pdf_non_pdf", "passed", duration, details={"success": success})
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_download_pdf_non_pdf", "failed", duration, str(e))
        raise

# 测试EPUB创建
@patch('pdf2epub_paddle.epub')
def test_create_epub(mock_epub):
    """测试EPUB创建功能"""
    start_time = time.time()
    try:
        # 模拟epub模块
        mock_book = MagicMock()
        mock_epub.EpubBook.return_value = mock_book
        mock_epub.write_epub = MagicMock()
        mock_epub.EpubItem = MagicMock()
        mock_epub.EpubHtml = MagicMock()
        mock_epub.EpubNcx = MagicMock()
        mock_epub.EpubNav = MagicMock()
        
        # 模拟API结果
        test_results = [
            {
                "result": {
                    "layoutParsingResults": [
                        {
                            "markdown": {
                                "text": "# Chapter 1 Introduction\nSome text",
                                "images": {}
                            }
                        }
                    ]
                }
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_dir = os.path.join(temp_dir, "images")
            os.makedirs(image_dir)
            output_file = os.path.join(temp_dir, "test.epub")
            
            # 创建EPUB
            create_epub(
                "Test Book",
                test_results,
                output_file,
                image_dir
            )
            
            # 验证epub.write_epub被调用
            mock_epub.write_epub.assert_called_once()
            duration = time.time() - start_time
            report_generator.add_result("test_create_epub", "passed", duration)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_create_epub", "failed", duration, str(e))
        raise

# 测试API调用
@patch('pdf2epub_paddle.requests.post')
def test_parse_pdf_chunk(mock_post):
    """测试PDF块解析功能"""
    start_time = time.time()
    try:
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "layoutParsingResults": []
            }
        }
        mock_post.return_value = mock_response
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            # 写入有效的PDF头
            temp_file.write(b"%PDF-1.4\n%e2e3cfd3\n")
            temp_file_path = temp_file.name
        
        try:
            # 解析PDF块
            result = parse_pdf_chunk(temp_file_path, "test_token")
            assert result is not None
            assert "result" in result
            duration = time.time() - start_time
            report_generator.add_result("test_parse_pdf_chunk", "passed", duration)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_parse_pdf_chunk", "failed", duration, str(e))
        raise

@patch('pdf2epub_paddle.requests.post')
def test_parse_pdf_chunk_api_error(mock_post):
    """测试API错误情况"""
    start_time = time.time()
    try:
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "error": "API Error"
        }
        mock_post.return_value = mock_response
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4\n%e2e3cfd3\n")
            temp_file_path = temp_file.name
        
        try:
            # 解析PDF块
            result = parse_pdf_chunk(temp_file_path, "test_token")
            assert result is None
            duration = time.time() - start_time
            report_generator.add_result("test_parse_pdf_chunk_api_error", "passed", duration)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_parse_pdf_chunk_api_error", "failed", duration, str(e))
        raise

@patch('pdf2epub_paddle.requests.post')
def test_parse_pdf_chunk_network_error(mock_post):
    """测试网络错误情况"""
    start_time = time.time()
    try:
        # 模拟网络错误
        mock_post.side_effect = Exception("Network Error")
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4\n%e2e3cfd3\n")
            temp_file_path = temp_file.name
        
        try:
            # 解析PDF块
            result = parse_pdf_chunk(temp_file_path, "test_token")
            assert result is None
            duration = time.time() - start_time
            report_generator.add_result("test_parse_pdf_chunk_network_error", "passed", duration)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        duration = time.time() - start_time
        report_generator.add_result("test_parse_pdf_chunk_network_error", "failed", duration, str(e))
        raise
