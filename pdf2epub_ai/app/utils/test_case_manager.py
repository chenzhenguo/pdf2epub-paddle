import os
import json
from typing import List, Dict, Any, Optional
from app.utils.logger import logger


class TestCase:
    """
    Test case class for PDF to EPUB conversion testing
    """
    def __init__(self, test_id: str, name: str, description: str, pdf_source: str, 
                 is_online: bool = False, expected_title: Optional[str] = None, 
                 expected_author: Optional[str] = None, tags: List[str] = None):
        """
        Initialize test case
        
        Args:
            test_id: Unique test case ID
            name: Test case name
            description: Test case description
            pdf_source: Path to local PDF or URL to online PDF
            is_online: Whether the PDF is from an online source
            expected_title: Expected book title
            expected_author: Expected book author
            tags: List of tags for categorization
        """
        self.test_id = test_id
        self.name = name
        self.description = description
        self.pdf_source = pdf_source
        self.is_online = is_online
        self.expected_title = expected_title
        self.expected_author = expected_author
        self.tags = tags or []
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
            "pdf_source": self.pdf_source,
            "is_online": self.is_online,
            "expected_title": self.expected_title,
            "expected_author": self.expected_author,
            "tags": self.tags,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """
        Create test case from dictionary
        
        Args:
            data: Dictionary with test case data
            
        Returns:
            TestCase instance
        """
        return cls(
            test_id=data.get("test_id"),
            name=data.get("name"),
            description=data.get("description"),
            pdf_source=data.get("pdf_source"),
            is_online=data.get("is_online", False),
            expected_title=data.get("expected_title"),
            expected_author=data.get("expected_author"),
            tags=data.get("tags", [])
        )


class TestCaseManager:
    """
    Test case management system
    """
    def __init__(self, test_dir: str = "./test_cases"):
        """
        Initialize test case manager
        
        Args:
            test_dir: Directory to store test cases
        """
        self.test_dir = test_dir
        os.makedirs(self.test_dir, exist_ok=True)
    
    def save_test_case(self, test_case: TestCase) -> bool:
        """
        Save test case to file
        
        Args:
            test_case: TestCase instance
            
        Returns:
            True if saved successfully
        """
        try:
            file_path = os.path.join(self.test_dir, f"{test_case.test_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_case.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Test case saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving test case: {str(e)}")
            return False
    
    def load_test_case(self, test_id: str) -> Optional[TestCase]:
        """
        Load test case from file
        
        Args:
            test_id: Test case ID
            
        Returns:
            TestCase instance or None if not found
        """
        try:
            file_path = os.path.join(self.test_dir, f"{test_id}.json")
            if not os.path.exists(file_path):
                logger.warning(f"Test case not found: {test_id}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_case = TestCase.from_dict(data)
            logger.info(f"Test case loaded: {test_id}")
            return test_case
        except Exception as e:
            logger.error(f"Error loading test case: {str(e)}")
            return None
    
    def list_test_cases(self, tags: List[str] = None) -> List[TestCase]:
        """
        List all test cases
        
        Args:
            tags: Filter test cases by tags
            
        Returns:
            List of TestCase instances
        """
        test_cases = []
        
        try:
            for file in os.listdir(self.test_dir):
                if file.endswith('.json'):
                    test_id = file.split('.')[0]
                    test_case = self.load_test_case(test_id)
                    if test_case:
                        # Filter by tags if provided
                        if tags:
                            if any(tag in test_case.tags for tag in tags):
                                test_cases.append(test_case)
                        else:
                            test_cases.append(test_case)
            
            logger.info(f"Found {len(test_cases)} test cases")
            return test_cases
        except Exception as e:
            logger.error(f"Error listing test cases: {str(e)}")
            return []
    
    def delete_test_case(self, test_id: str) -> bool:
        """
        Delete test case
        
        Args:
            test_id: Test case ID
            
        Returns:
            True if deleted successfully
        """
        try:
            file_path = os.path.join(self.test_dir, f"{test_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Test case deleted: {test_id}")
                return True
            else:
                logger.warning(f"Test case not found: {test_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting test case: {str(e)}")
            return False
    
    def get_test_case_by_tags(self, tags: List[str]) -> List[TestCase]:
        """
        Get test cases by tags
        
        Args:
            tags: List of tags
            
        Returns:
            List of TestCase instances
        """
        return self.list_test_cases(tags)
    
    def get_online_test_cases(self) -> List[TestCase]:
        """
        Get online test cases
        
        Returns:
            List of online TestCase instances
        """
        all_cases = self.list_test_cases()
        return [case for case in all_cases if case.is_online]
    
    def get_local_test_cases(self) -> List[TestCase]:
        """
        Get local test cases
        
        Returns:
            List of local TestCase instances
        """
        all_cases = self.list_test_cases()
        return [case for case in all_cases if not case.is_online]
