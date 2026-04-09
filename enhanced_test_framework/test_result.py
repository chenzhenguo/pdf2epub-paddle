import time
from typing import Dict, Any, Optional, List


class TestResult:
    """
    Enhanced test result class with detailed information
    """
    def __init__(self, test_id: str, test_name: str, success: bool, 
                 message: str, duration: float, output: Optional[Any] = None,
                 error: Optional[str] = None, logs: Optional[List[str]] = None):
        """
        Initialize test result
        
        Args:
            test_id: Test case ID
            test_name: Test case name
            success: Whether test passed
            message: Test message
            duration: Test duration in seconds
            output: Test output data
            error: Error message if test failed
            logs: List of log messages generated during test
        """
        self.test_id = test_id
        self.test_name = test_name
        self.success = success
        self.message = message
        self.duration = duration
        self.output = output
        self.error = error
        self.logs = logs or []
        self.timestamp = time.time()
        self.start_time = time.time() - duration
    
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
            "output": self.output,
            "error": self.error,
            "logs": self.logs,
            "timestamp": self.timestamp,
            "start_time": self.start_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """
        Create test result from dictionary
        
        Args:
            data: Dictionary with test result data
            
        Returns:
            TestResult instance
        """
        return cls(
            test_id=data.get("test_id"),
            test_name=data.get("test_name"),
            success=data.get("success"),
            message=data.get("message"),
            duration=data.get("duration"),
            output=data.get("output"),
            error=data.get("error"),
            logs=data.get("logs", [])
        )
