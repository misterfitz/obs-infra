#!/usr/bin/env python3
import click
import logging
import sys
import os
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Observability Infrastructure Testing Suite
    
    A comprehensive testing tool for AWS observability infrastructure
    including EKS, Prometheus, and Grafana.
    """
    pass

@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file')
@click.option('--endpoint-url', help='AWS endpoint URL (for localstack)')
@click.option('--region', default='us-gov-west-1', help='AWS region')
def setup(config, endpoint_url, region):
    """Initialize test environment"""
    click.echo(f"Setting up test environment in {region}")
    
    if endpoint_url:
        click.echo(f"Using endpoint URL: {endpoint_url}")
        os.environ['AWS_ENDPOINT_URL'] = endpoint_url
    
    # Implementation of setup logic
    click.echo("Setup complete")

@cli.command()
@click.option('--base-url', required=True, help='Base URL for API testing')
@click.option('--endpoints', required=True, multiple=True, help='Endpoints to test')
@click.option('--rounds', default=10, help='Number of rounds per parameter')
@click.option('--output', default='fuzz_results.json', help='Output file for results')
def fuzz(base_url, endpoints, rounds, output):
    """Run API fuzzing tests"""
    click.echo(f"Starting API fuzzing against {base_url}")
    
    try:
        # Import fuzzer dynamically (allows CLI to load even if dependency missing)
        from fuzz.api_fuzzer import ApiFuzzer
        
        fuzzer = ApiFuzzer(base_url=base_url, endpoints=endpoints)
        
        click.echo(f"Testing {len(endpoints)} endpoints with {rounds} rounds each")
        results = fuzzer.fuzz_all_endpoints(rounds_per_endpoint=rounds)
        
        fuzzer.export_results(output)
        click.echo(f"Results exported to {output}")
        
        click.echo(f"Summary: {results.get('total_tests', 0)} tests, "
                f"{results.get('success', 0)} successful, {results.get('failures', 0)} failures")
    except ImportError as e:
        click.echo(f"Error: Required module not found: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error running fuzz tests: {e}")
        sys.exit(1)

@cli.command()
@click.option('--region', default='us-gov-west-1', help='AWS region')
@click.option('--output-csv', default='compliance_report.csv', help='Output CSV file')
@click.option('--output-html', default='compliance_report.html', help='Output HTML file')
def compliance_scan(region, output_csv, output_html):
    """Run security compliance scan"""
    click.echo(f"Starting security compliance scan in {region}")
    
    try:
        from security.compliance_scanner import SecurityComplianceScanner
        
        scanner = SecurityComplianceScanner(region=region)
        click.echo(f"Running {len(scanner.rules)} compliance checks")
        
        results = scanner.scan_all()
        
        scanner.export_results_csv(output_csv)
        scanner.export_results_html(output_html)
        
        click.echo(f"Scan complete. Reports exported to {output_csv} and {output_html}")
        click.echo(f"Summary: {results['summary']['passed']} passed, "
                f"{results['summary']['failed']} failed, "
                f"{results['summary']['warnings']} warnings, "
                f"{results['summary']['errors']} errors")
    except ImportError as e:
        click.echo(f"Error: Required module not found: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error running compliance scan: {e}")
        sys.exit(1)

@cli.command()
@click.option('--cluster-name', required=True, help='EKS cluster name')
@click.option('--region', default='us-gov-west-1', help='AWS region')
@click.option('--endpoint-url', help='AWS endpoint URL (for localstack)')
def validate_infrastructure(cluster_name, region, endpoint_url):
    """Validate the infrastructure setup"""
    click.echo(f"Validating infrastructure for cluster {cluster_name} in {region}")
    
    if endpoint_url:
        click.echo(f"Using endpoint URL: {endpoint_url}")
        os.environ['AWS_ENDPOINT_URL'] = endpoint_url
    
    try:
        from tests.eks_integration_test import EksIntegrationTester
        
        tester = EksIntegrationTester(
            cluster_name=cluster_name,
            region=region
        )
        
        click.echo("Running all validation tests...")
        results = tester.run_all_tests()
        
        if results["all_passed"]:
            click.echo("All validation tests PASSED!")
        else:
            click.echo("Some validation tests FAILED!")
            
        for test_name, test_result in results["tests"].items():
            status = "PASSED" if test_result["success"] else "FAILED"
            duration = f"{test_result['duration_ms']:.2f}ms"
            click.echo(f"  {test_name}: {status} ({duration})")
        
        # Export results
        output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        click.echo(f"Results exported to {output_file}")
        
        # Exit with error code if tests failed
        if not results["all_passed"]:
            sys.exit(1)
            
    except ImportError as e:
        click.echo(f"Error: Required module not found: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error validating infrastructure: {e}")
        sys.exit(1)

@cli.command()
@click.option('--terraform-dir', default='./terraform', help='Terraform directory')
@click.option('--environment', default='dev', help='Environment to deploy')
@click.option('--endpoint-url', help='AWS endpoint URL (for localstack)')
def deploy(terraform_dir, environment, endpoint_url):
    """Deploy infrastructure using Terraform"""
    click.echo(f"Deploying infrastructure to {environment} environment")
    
    if endpoint_url:
        click.echo(f"Using endpoint URL: {endpoint_url}")
        os.environ['TF_VAR_endpoint_url'] = endpoint_url
    
    try:
        # Create environment directory if it doesn't exist
        env_dir = os.path.join(terraform_dir, 'environments', environment)
        if not os.path.exists(env_dir):
            click.echo(f"Creating environment directory: {env_dir}")
            os.makedirs(env_dir, exist_ok=True)
        
        # Change to environment directory
        os.chdir(env_dir)
        
        # Run Terraform
        click.echo("Initializing Terraform...")
        os.system('terraform init')
        
        click.echo("Planning Terraform deployment...")
        os.system('terraform plan -out=tfplan')
        
        click.echo("Applying Terraform plan...")
        os.system('terraform apply -auto-approve tfplan')
        
        click.echo(f"Infrastructure deployed to {environment} environment")
    except Exception as e:
        click.echo(f"Error deploying infrastructure: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()