import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pdf2epub_paddle import download_pdf

@patch('pdf2epub_paddle.requests.get')
@patch('builtins.open', new_callable=MagicMock)
def test_download_pdf(mock_open, mock_get):
    """测试 PDF 文件下载功能"""
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
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file_path = temp_file.name
    
    try:
        # 使用新的 download_pdf 函数下载 PDF 文件
        success = download_pdf("https://example.com/test.pdf", temp_file_path)
        assert success, "Failed to download PDF"
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
