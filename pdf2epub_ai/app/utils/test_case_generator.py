import uuid
from app.utils.test_case_manager import TestCase, TestCaseManager
from app.utils.logger import logger


def generate_test_cases():
    """
    Generate comprehensive test cases
    """
    manager = TestCaseManager()
    
    # Clear existing test cases to avoid duplicates
    existing_cases = manager.list_test_cases()
    for case in existing_cases:
        manager.delete_test_case(case.test_id)
    
    # Test cases for online PDF sources
    online_test_cases = [
        TestCase(
            test_id=f"online_{uuid.uuid4()}",
            name="Sample PDF Document",
            description="Sample PDF document from Adobe",
            pdf_source="https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf",
            is_online=True,
            expected_title="Sample PDF Document",
            tags=["online", "sample", "basic"]
        )
    ]
    
    # Combine all test cases
    all_test_cases = online_test_cases
    
    # Save test cases
    for test_case in all_test_cases:
        success = manager.save_test_case(test_case)
        if success:
            logger.info(f"Test case saved: {test_case.name}")
        else:
            logger.error(f"Failed to save test case: {test_case.name}")
    
    logger.info(f"Generated {len(all_test_cases)} test cases")
    return all_test_cases


if __name__ == "__main__":
    generate_test_cases()
