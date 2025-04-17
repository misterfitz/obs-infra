# Observability Infrastructure Test Suite

This directory contains a comprehensive testing suite for the AWS observability infrastructure stack.

## Components

- **Fuzz Testing** - API fuzzing for vulnerability detection
- **Load Testing** - Simulate high load on Grafana and Prometheus
- **Security Testing** - Basic security and compliance checks
- **Metrics Generation** - Generate test metrics for Prometheus
- **Integration Testing** - Validate the entire infrastructure stack

## Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run all tests:
   ```
   python src/test_runner.py
   ```

3. Run specific test types:
   ```
   python src/cli.py fuzz --base-url http://localhost:4566 --endpoints /api/v1/metrics
   python src/cli.py compliance-scan --region us-gov-west-1
   ```

## Directory Structure

- `src/` - Source code for the test suite
  - `fuzz/` - API fuzzing for vulnerability detection
  - `data_generator/` - Test data generation
  - `load_test/` - Load testing
  - `security/` - Security and compliance testing
  - `tests/` - Integration testing
  - `utils/` - Utility functions
- `dashboards/` - Grafana dashboards
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.11+
- AWS CLI configured with appropriate credentials
- Docker and Docker Compose for local testing
- Access to AWS GovCloud resources