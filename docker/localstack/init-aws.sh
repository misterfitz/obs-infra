#!/bin/bash
set -e

echo "Initializing LocalStack AWS resources..."

# Create EKS cluster
echo "Creating EKS cluster..."
awslocal eks create-cluster \
  --name obs-eks \
  --role-arn arn:aws:iam::000000000000:role/eks-cluster-role \
  --resources-vpc-config subnetIds=subnet-12345,subnet-67890,securityGroupIds=sg-12345

# Create S3 bucket for Terraform state
echo "Creating S3 bucket for Terraform state..."
awslocal s3 mb s3://terraform-state-bucket

# Create IAM roles
echo "Creating IAM roles..."
awslocal iam create-role \
  --role-name eks-cluster-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"eks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

awslocal iam create-role \
  --role-name eks-node-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

# Create VPC and subnets
echo "Creating VPC and subnets..."
VPC_ID=$(awslocal ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
SUBNET1_ID=$(awslocal ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --query 'Subnet.SubnetId' --output text)
SUBNET2_ID=$(awslocal ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --query 'Subnet.SubnetId' --output text)

# Create security groups
echo "Creating security groups..."
SG_ID=$(awslocal ec2 create-security-group --group-name eks-cluster-sg --description "EKS Cluster SG" --vpc-id $VPC_ID --query 'GroupId' --output text)

# Create CloudWatch log group
echo "Creating CloudWatch log group..."
awslocal logs create-log-group --log-group-name /aws/eks/obs-eks/cluster

# Create SNS topics for alerts
echo "Creating SNS topics for alerts..."
awslocal sns create-topic --name observability-alerts

echo "LocalStack AWS resources initialized successfully!"