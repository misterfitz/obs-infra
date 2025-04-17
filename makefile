.PHONY: setup start stop test terraform-init terraform-apply terraform-destroy lint format

# Variables
COMPOSE_FILE=docker-compose.yml

# Setup the project
setup:
	@echo "Setting up the project..."
	pip install -r test-suite/requirements.txt
	cd terraform && terraform init

# Start all containers
start:
	@echo "Starting all containers..."
	docker-compose -f $(COMPOSE_FILE) up -d

# Stop all containers
stop:
	@echo "Stopping all containers..."
	docker-compose -f $(COMPOSE_FILE) down

# Run all tests
test:
	@echo "Running all tests..."
	docker-compose -f $(COMPOSE_FILE) exec test-runner financial-test compliance-scan --region us-gov-west-1
	docker-compose -f $(COMPOSE_FILE) exec test-runner financial-test fuzz --base-url http://localstack:4566 --endpoints /api/v1/payments /api/v1/accounts

# Initialize Terraform
terraform-init:
	@echo "Initializing Terraform..."
	cd terraform && terraform init

# Apply Terraform configuration
terraform-apply:
	@echo "Applying Terraform configuration..."
	cd terraform && terraform apply

# Destroy Terraform resources
terraform-destroy:
	@echo "Destroying Terraform resources..."
	cd terraform && terraform destroy

# Lint the code
lint:
	@echo "Linting the code..."
	cd test-suite && flake8 src tests

# Format the code
format:
	@echo "Formatting the code..."
	cd test-suite && black src tests