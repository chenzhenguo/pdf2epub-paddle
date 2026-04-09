#!/usr/bin/env python3
"""
Test file for PDFDownloader class
"""

import os
import tempfile
import shutil
from unittest import TestCase, mock
from app.utils.pdf_downloader import PDFDownloader


class TestPDFDownloader(TestCase):
    """Test cases for PDFDownloader class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.downloader = PDFDownloader(cache_dir=self.test_dir, max_retries=2, retry_delay=1)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test initialization of PDFDownloader"""
        self.assertEqual(self.downloader.cache_dir, self.test_dir)
        self.assertEqual(self.downloader.max_retries, 2)
        self.assertEqual(self.downloader.retry_delay, 1)
        # Verify cache directory was created
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        url = "https://example.com/test.pdf"
        cache_key = self.downloader._get_cache_key(url)
        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 32)  # MD5 hash length
    
    def test_get_cache_path(self):
        """Test cache path generation"""
        url = "https://example.com/test.pdf"
        cache_path = self.downloader._get_cache_path(url)
        self.assertIsInstance(cache_path, str)
        self.assertTrue(cache_path.endswith('.pdf'))
        self.assertTrue(os.path.dirname(cache_path) == self.test_dir)
    
    @mock.patch('requests.get')
    def test_download_success(self, mock_get):
        """Test successful PDF download"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.iter_content.return_value = [b'%PDF-1.4', b'%%EOF']
        mock_get.return_value = mock_response
        
        url = "https://example.com/test.pdf"
        result = self.downloader.download(url)
        
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
        mock_get.assert_called_once_with(url, timeout=30, stream=True, verify=False)
    
    @mock.patch('requests.get')
    def test_download_not_pdf(self, mock_get):
        """Test download when response is not PDF"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response
        
        url = "https://example.com/not-pdf.html"
        result = self.downloader.download(url)
        
        self.assertIsNone(result)
    
    @mock.patch('requests.get')
    def test_download_http_error(self, mock_get):
        """Test download with HTTP error"""
        # Import the correct exception type
        import requests
        # Mock response
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("HTTP Error")
        mock_get.return_value = mock_response
        
        url = "https://example.com/error"
        result = self.downloader.download(url)
        
        self.assertIsNone(result)
        # Verify it retried the specified number of times
        self.assertEqual(mock_get.call_count, 3)  # 1 initial + 2 retries
    
    def test_get_pdf_local_file(self):
        """Test get_pdf with local file"""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4')
            local_pdf = f.name
        
        try:
            result = self.downloader.get_pdf(local_pdf)
            self.assertEqual(result, local_pdf)
        finally:
            os.unlink(local_pdf)
    
    def test_get_pdf_local_non_pdf(self):
        """Test get_pdf with local non-PDF file"""
        # Create a temporary non-PDF file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Test')
            local_txt = f.name
        
        try:
            result = self.downloader.get_pdf(local_txt)
            self.assertIsNone(result)
        finally:
            os.unlink(local_txt)
    
    @mock.patch('app.utils.pdf_downloader.PDFDownloader.download')
    def test_get_pdf_url(self, mock_download):
        """Test get_pdf with URL"""
        mock_download.return_value = "/path/to/cached.pdf"
        
        url = "https://example.com/test.pdf"
        result = self.downloader.get_pdf(url)
        
        self.assertEqual(result, "/path/to/cached.pdf")
        mock_download.assert_called_once_with(url, 30)
    
    def test_get_pdf_cloud_storage(self):
        """Test get_pdf with cloud storage path"""
        # This should return None as cloud storage is not implemented
        result = self.downloader.get_pdf("s3://bucket/path/to.pdf")
        self.assertIsNone(result)
    
    def test_get_pdf_unknown_source(self):
        """Test get_pdf with unknown source type"""
        result = self.downloader.get_pdf("unknown://source")
        self.assertIsNone(result)
    
    def test_clear_cache(self):
        """Test clear_cache method"""
        # Create a test PDF file in the cache directory
        test_pdf = os.path.join(self.test_dir, "test.pdf")
        with open(test_pdf, 'w') as f:
            f.write("test")
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_pdf))
        
        # Clear cache
        result = self.downloader.clear_cache()
        self.assertTrue(result)
        
        # Verify file was removed
        self.assertFalse(os.path.exists(test_pdf))
    
    def test_get_cache_info(self):
        """Test get_cache_info method"""
        # Create test PDF files in the cache directory
        for i in range(3):
            test_pdf = os.path.join(self.test_dir, f"test{i}.pdf")
            with open(test_pdf, 'w') as f:
                f.write(f"test{i}")
        
        info = self.downloader.get_cache_info()
        self.assertEqual(info["cache_dir"], self.test_dir)
        self.assertEqual(info["file_count"], 3)
        self.assertGreater(info["total_size"], 0)
        self.assertEqual(len(info["files"]), 3)
        self.assertEqual(info["status"], "Success")


if __name__ == '__main__':
    import unittest
    unittest.main()
