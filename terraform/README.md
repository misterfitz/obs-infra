# Observability Infrastructure Terraform

This directory contains Terraform modules to deploy a complete observability infrastructure stack in AWS GovCloud.

## Components

- **VPC** - Network infrastructure for secure communication
- **EKS Cluster** - Managed Kubernetes for container orchestration
- **AWS Managed Prometheus** - Metrics collection and storage
- **AWS Managed Grafana** - Visualization and dashboarding
- **IAM Roles and Permissions** - Secure access control

## Usage

1. Initialize Terraform:
   ```
   terraform init
   ```

2. Preview changes:
   ```
   terraform plan
   ```

3. Apply the configuration:
   ```
   terraform apply
   ```

4. Destroy resources when done:
   ```
   terraform destroy
   ```

## Modules

- `vpc` - Virtual Private Cloud with public and private subnets
- `eks` - Elastic Kubernetes Service cluster
- `amp` - AWS Managed Prometheus
- `amg` - AWS Managed Grafana
- `iam` - Identity and Access Management roles and policies

## Requirements

- Terraform >= 1.0.0
- AWS CLI configured with appropriate credentials
- Administrative access to AWS GovCloud