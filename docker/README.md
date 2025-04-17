# Docker Configuration for Observability Infrastructure

This directory contains Docker configurations for local development and testing.

## Components

- **LocalStack** - AWS service emulator for local testing
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboarding
- **Test Runner** - Container for running tests

## Directory Structure

- `localstack/` - Configuration for LocalStack
  - `init-aws.sh` - Initialization script for AWS resources
- `prometheus/` - Configuration for Prometheus
  - `prometheus.yml` - Prometheus configuration
- `grafana/` - Configuration for Grafana
  - `provisioning/` - Grafana provisioning
- `test-runner/` - Configuration for test runner
  - `Dockerfile` - Dockerfile for test runner

## Usage

Use Docker Compose to start all containers:

```
docker-compose up -d
```

To run tests in the test runner container:

```
docker-compose exec test-runner obs-test [command]
```

Available commands:

- `fuzz` - Run API fuzzing tests
- `compliance-scan` - Run compliance scanner
- `validate-infrastructure` - Validate infrastructure
- `deploy` - Deploy infrastructure using Terraform