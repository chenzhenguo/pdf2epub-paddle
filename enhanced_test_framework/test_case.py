import os
from typing import List, Dict, Any, Optional


class TestCase:
    """
    Enhanced test case class with dependency management
    """
    def __init__(self, test_id: str, name: str, description: str, 
                 test_function: callable, dependencies: List[str] = None, 
                 tags: List[str] = None, timeout: int = 300):
        """
        Initialize test case
        
        Args:
            test_id: Unique test case ID
            name: Test case name
            description: Test case description
            test_function: Callable function that executes the test
            dependencies: List of test IDs that this test depends on
            tags: List of tags for categorization
            timeout: Test timeout in seconds
        """
        self.test_id = test_id
        self.name = name
        self.description = description
        self.test_function = test_function
        self.dependencies = dependencies or []
        self.tags = tags or []
        self.timeout = timeout
        self.created_at = os.path.getmtime(__file__) if os.path.exists(__file__) else None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert test case to dictionary
        
        Returns:
            Dictionary representation of test case
        """
        return {
            "test_id": self.test_id,
            "name": self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "timeout": self.timeout,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], test_function: callable) -> 'TestCase':
        """
        Create test case from dictionary
        
        Args:
            data: Dictionary with test case data
            test_function: Callable function that executes the test
            
        Returns:
            TestCase instance
        """
        return cls(
            test_id=data.get("test_id"),
            name=data.get("name"),
            description=data.get("description"),
            test_function=test_function,
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            timeout=data.get("timeout", 300)
        )
    
    def run(self) -> Any:
        """
        Run the test case
        
        Returns:
            Result of the test function
        """
        return self.test_function()
