FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    jq \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Install Terraform
RUN curl -fsSL https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

# Configure AWS CLI for localstack
RUN aws configure set aws_access_key_id test \
    && aws configure set aws_secret_access_key test \
    && aws configure set region us-gov-west-1 \
    && aws configure set output json

# Copy requirements and install dependencies
COPY test-suite/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the CLI script
COPY test-suite/src/cli.py /usr/local/bin/financial-test
RUN chmod +x /usr/local/bin/financial-test

# Set up environment
ENV PYTHONPATH=/app/test-suite

# Set entrypoint
ENTRYPOINT ["financial-test"]