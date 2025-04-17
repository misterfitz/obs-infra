# Observability Infrastructure Stack

A comprehensive infrastructure and testing suite for AWS observability stack including EKS, Prometheus, and Grafana.

## Features

- **Infrastructure as Code** - Terraform modules for AWS infrastructure
- **API Fuzzing** - Test API endpoints for security vulnerabilities
- **Load Testing** - Simulate high load on Grafana and Prometheus
- **Compliance Scanning** - Check AWS resources against security best practices
- **Disaster Recovery Testing** - Simulate failure scenarios and verify recovery
- **Metric Generation** - Generate test metrics for Prometheus
- **Integration Testing** - Validate the entire infrastructure stack

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- AWS CLI
- Terraform 1.0+

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/misterfitz/obs-infra.git
   cd obs-infra
   ```

2. Set up the project:
   ```bash
   make setup
   ```

3. Start the local development environment:
   ```bash
   make start
   ```

### Running Tests

Run all tests:
```bash
make test
```

Run specific test:
```bash
docker-compose exec test-runner obs-test fuzz --base-url http://localstack:4566 --endpoints /api/v1/metrics
```

### Deploying Infrastructure

Deploy to development environment:
```bash
make terraform-apply
```

## Project Structure

- `terraform/` - Terraform modules and configurations
- `test-suite/` - Python test suite
- `dashboards/` - Grafana dashboards
- `docker/` - Docker configurations
- `.github/` - GitHub workflows and CI/CD

## Infrastructure Components

The Terraform code provisions the following components:

1. **VPC with Public and Private Subnets** - Network infrastructure for secure communication
2. **EKS Cluster** - Managed Kubernetes for container orchestration
3. **AWS Managed Prometheus** - Metrics collection and storage
4. **AWS Managed Grafana** - Visualization and dashboarding
5. **IAM Roles and Permissions** - Secure access control

## Testing Capabilities

### Security Testing

- API fuzzing for vulnerability detection
- Compliance scanning against best practices
- Security group validation

### Performance Testing

- Load testing for Grafana
- Metrics generation for Prometheus
- Capacity testing for EKS

### Disaster Recovery Testing

- Node failure simulation
- AZ failure simulation
- Database failover testing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Structure 

```
obs-infra-testing/
├── .github/                       # GitHub workflows and CI/CD
│   └── workflows/
│       ├── ci.yml                 # CI workflow 
│       └── release.yml            # Release workflow
├── docker/                        # Docker configurations
│   ├── grafana/                   # Grafana container config
│   ├── prometheus/                # Prometheus container config
│   ├── localstack/                # Localstack configuration
│   └── test-runner/               # Test runner container
├── terraform/                     # Terraform modules
│   ├── modules/                   # Reusable modules
│   │   ├── vpc/                   # VPC module
│   │   ├── eks/                   # EKS module
│   │   ├── amp/                   # AWS Managed Prometheus module
│   │   ├── amg/                   # AWS Managed Grafana module
│   │   ├── iam/                   # IAM roles and permissions
│   │   ├── alerting/              # Alerting configuration
│   │   └── cost_dashboard/        # Cost optimization dashboard
│   ├── environments/              # Environment configurations
│   │   ├── dev/                   # Development environment
│   │   ├── test/                  # Test environment
│   │   └── prod/                  # Production environment
│   ├── main.tf                    # Main Terraform configuration
│   ├── variables.tf               # Variables definitions
│   ├── outputs.tf                 # Output definitions
│   ├── providers.tf               # Provider configurations
│   └── versions.tf                # Version constraints
├── test-suite/                    # Python test suite
│   ├── src/                       # Source code
│   │   ├── fuzz/                  # API fuzzing
│   │   ├── data_generator/        # Test data generation
│   │   ├── load_test/             # Load testing
│   │   ├── security/              # Security compliance
│   │   ├── dr/                    # Disaster recovery
│   │   ├── utils/                 # Utilities
│   │   └── cli.py                 # Command-line interface
│   ├── tests/                     # Tests for the test suite itself
│   ├── pyproject.toml             # Python project configuration
│   ├── setup.py                   # Package setup
│   └── requirements.txt           # Dependencies
├── dashboards/                    # Grafana dashboards
│   ├── metrics.json     # Financial metrics dashboard
│   ├── infrastructure.json        # Infrastructure dashboard
│   ├── security.json              # Security dashboard
│   └── cost_optimization.json     # Cost optimization dashboard
├── docker-compose.yml             # Docker Compose configuration
├── Makefile                       # Makefile for common operations
├── README.md                      # Project README
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                        # License information
└── CHANGELOG.md                   # Version changelog
```