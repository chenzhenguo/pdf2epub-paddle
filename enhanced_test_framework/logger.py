import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Optional


class EnhancedLogger:
    """
    Enhanced logger class with test-specific logging capabilities
    """
    def __init__(self, name: str = "test_framework", log_dir: str = "./logs"):
        """
        Initialize enhanced logger
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
        """
        self.name = name
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler with rotation
        log_file = os.path.join(self.log_dir, f"{name}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, test_id: Optional[str] = None):
        """
        Log debug message
        
        Args:
            message: Log message
            test_id: Test case ID (optional)
        """
        if test_id:
            self.logger.debug(f"[{test_id}] {message}")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, test_id: Optional[str] = None):
        """
        Log info message
        
        Args:
            message: Log message
            test_id: Test case ID (optional)
        """
        if test_id:
            self.logger.info(f"[{test_id}] {message}")
        else:
            self.logger.info(message)
    
    def warning(self, message: str, test_id: Optional[str] = None):
        """
        Log warning message
        
        Args:
            message: Log message
            test_id: Test case ID (optional)
        """
        if test_id:
            self.logger.warning(f"[{test_id}] {message}")
        else:
            self.logger.warning(message)
    
    def error(self, message: str, test_id: Optional[str] = None):
        """
        Log error message
        
        Args:
            message: Log message
            test_id: Test case ID (optional)
        """
        if test_id:
            self.logger.error(f"[{test_id}] {message}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, test_id: Optional[str] = None):
        """
        Log critical message
        
        Args:
            message: Log message
            test_id: Test case ID (optional)
        """
        if test_id:
            self.logger.critical(f"[{test_id}] {message}")
        else:
            self.logger.critical(message)
    
    def log_test_start(self, test_id: str, test_name: str):
        """
        Log test start
        
        Args:
            test_id: Test case ID
            test_name: Test case name
        """
        self.info(f"Starting test: {test_name}", test_id)
    
    def log_test_end(self, test_id: str, test_name: str, success: bool, duration: float):
        """
        Log test end
        
        Args:
            test_id: Test case ID
            test_name: Test case name
            success: Whether test passed
            duration: Test duration in seconds
        """
        status = "PASSED" if success else "FAILED"
        self.info(f"Test {status}: {test_name} (duration: {duration:.2f}s)", test_id)
    
    def log_test_error(self, test_id: str, test_name: str, error: str):
        """
        Log test error
        
        Args:
            test_id: Test case ID
            test_name: Test case name
            error: Error message
        """
        self.error(f"Test failed: {test_name} - {error}", test_id)


# Create global logger instance
logger = EnhancedLogger()
