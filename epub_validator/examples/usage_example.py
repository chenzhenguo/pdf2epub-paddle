#!/usr/bin/env python3
"""
Example script demonstrating how to use the EPUBValidator class
"""

from src.epub_validator import EPUBValidator
import sys

def validate_epub(epub_path):
    """Validate an EPUB file and print the results"""
    print(f"Validating EPUB: {epub_path}")
    print("=" * 60)
    
    # Create validator instance
    validator = EPUBValidator(epub_path)
    
    # Run all validation checks
    results = validator.validate_all()
    
    # Print results
    print("Validation Results:")
    print("-" * 60)
    
    for validation_type, (valid, errors, warnings) in results.items():
        status = "PASS" if valid else "FAIL"
        print(f"{validation_type.capitalize()}: {status}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        
        if errors:
            print("  Error details:")
            for error in errors:
                print(f"    - {error}")
        
        if warnings:
            print("  Warning details:")
            for warning in warnings:
                print(f"    - {warning}")
        print()
    
    # Print summary
    print("Summary:")
    print("-" * 60)
    print(validator.get_summary())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python usage_example.py <epub_file>")
        sys.exit(1)
    
    epub_file = sys.argv[1]
    validate_epub(epub_file)