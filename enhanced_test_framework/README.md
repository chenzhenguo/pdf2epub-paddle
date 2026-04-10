# Enhanced Test Framework

A comprehensive test framework with advanced reporting capabilities.

## Features

### Core Features
- **Test Case Management**: Create and manage test cases with dependencies, tags, and timeouts
- **Parallel Execution**: Run tests in parallel for faster execution
- **Dependency Management**: Automatically handle test dependencies
- **Timeout Handling**: Prevent long-running tests from blocking execution

### Advanced Reporting
- **Multiple Report Formats**: Generate reports in JSON, HTML, and CSV formats
- **Detailed Summary Statistics**: Includes success rate, duration metrics, and error distribution
- **Trend Analysis**: Analyze trends across multiple test runs
- **Run Comparison**: Compare test runs to identify improvements and regressions
- **Error Distribution**: Categorize and analyze test failures

## Usage

### Basic Usage

```python
from enhanced_test_framework.test_case import TestCase
from enhanced_test_framework.test_runner import TestRunner
from enhanced_test_framework.test_reporter import TestReporter

# Create test cases
def test_function():
    return "Test passed"

test_case = TestCase(
    test_id="test1",
    name="Test Case 1",
    description="Test case 1 description",
    test_function=test_function
)

# Run tests
test_runner = TestRunner(output_dir="./test_output")
test_runner.add_test_case(test_case)
results = test_runner.run_all_tests()

# Generate reports
test_reporter = TestReporter(output_dir="./test_reports")
report_paths = test_reporter.generate_report(results)

print(f"Reports generated: {report_paths}")
```

### Advanced Reporting

#### Trend Analysis

```python
# Analyze trends across multiple test runs
run1 = test_runner.run_all_tests()
# Make some changes to your code
run2 = test_runner.run_all_tests()
# Make more changes
run3 = test_runner.run_all_tests()

trend_data = test_reporter.analyze_trends([run1, run2, run3])
print(f"Trend analysis: {trend_data}")
```

#### Run Comparison

```python
# Compare two test runs
baseline = test_runner.run_all_tests()
# Make changes to your code
comparison = test_runner.run_all_tests()

comparison_data = test_reporter.compare_runs(baseline, comparison)
print(f"Run comparison: {comparison_data}")
```

## Report Formats

### JSON Report
- Comprehensive structured data
- Includes all test details and statistics
- Suitable for automated processing

### HTML Report
- Interactive, human-readable format
- Includes summary statistics and detailed test results
- Error distribution table for failure analysis

### CSV Report
- Tabular format for spreadsheet analysis
- Includes all test details in a structured format
- Easy to import into data analysis tools

## Enhanced Summary Statistics

The framework provides detailed summary statistics including:
- Total tests, passed, failed
- Success rate
- Average, minimum, and maximum test durations
- Duration standard deviation
- Error distribution by error type

## Testing

To run the test suite:

```bash
python -m pytest enhanced_test_framework/tests/test_framework.py -v
```

## License

[MIT License](LICENSE)
