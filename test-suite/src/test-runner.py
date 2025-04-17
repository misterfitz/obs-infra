#!/usr/bin/env python3
import logging
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRunner:
    """
    Main test runner for observability infrastructure tests
    
    This class coordinates the execution of different test types:
    - API Fuzzing tests
    - Load tests
    - Security compliance checks
    - Infrastructure validation
    - Prometheus metric generation
    
    It collects results from all tests and produces a consolidated report.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the test runner
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = {}
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Use default configuration
            self.config = {
                "api_tests": {
                    "enabled": True,
                    "base_url": "http://localhost:4566",
                    "endpoints": ["/api/v1/metrics", "/api/v1/query"],
                    "rounds": 5
                },
                "load_tests": {
                    "enabled": True,
                    "grafana_url": "http://localhost:3000",
                    "concurrent_users": 10,
                    "duration_seconds": 60
                },
                "security_tests": {
                    "enabled": True,
                    "region": "us-gov-west-1",
                    "endpoint_url": "http://localhost:4566"
                },
                "infrastructure_tests": {
                    "enabled": True,
                    "cluster_name": "obs-eks",
                    "region": "us-gov-west-1",
                    "endpoint_url": "http://localhost:4566"
                },
                "metric_generation": {
                    "enabled": True,
                    "push_gateway_url": "http://localhost:9091",
                    "duration_seconds": 30
                },
                "output": {
                    "report_file": "test_report.json",
                    "report_format": "json"
                }
            }
    
    def run_api_tests(self) -> Dict:
        """Run API fuzzing tests"""
        if not self.config.get("api_tests", {}).get("enabled", False):
            logger.info("API tests disabled, skipping")
            return {"status": "skipped"}
        
        logger.info("Running API fuzzing tests")
        
        try:
            from fuzz.api_fuzzer import ApiFuzzer
            
            config = self.config["api_tests"]
            fuzzer = ApiFuzzer(
                base_url=config["base_url"],
                endpoints=config["endpoints"]
            )
            
            results = fuzzer.fuzz_all_endpoints(
                rounds_per_endpoint=config.get("rounds", 5)
            )
            
            logger.info(f"API tests completed: {results['total_tests']} tests, "
                       f"{results['success']} successful, {results['failures']} failures")
            
            # Export results if configured
            output_file = config.get("output_file", "fuzz_results.json")
            fuzzer.export_results(output_file)
            
            return {
                "status": "completed",
                "summary": {
                    "total_tests": results["total_tests"],
                    "success": results["success"],
                    "failures": results["failures"],
                    "issues_count": len(results.get("issues", []))
                },
                "output_file": output_file
            }
        except Exception as e:
            logger.error(f"Error running API tests: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_load_tests(self) -> Dict:
        """Run load tests"""
        if not self.config.get("load_tests", {}).get("enabled", False):
            logger.info("Load tests disabled, skipping")
            return {"status": "skipped"}
        
        logger.info("Running load tests")
        
        try:
            from load_test.grafana_load import GrafanaLoadTester, LoadTestConfig
            
            config = self.config["load_tests"]
            
            # Get API key if available
            api_key = config.get("api_key", "")
            if not api_key and os.environ.get("GRAFANA_API_KEY"):
                api_key = os.environ.get("GRAFANA_API_KEY")
            
            test_config = LoadTestConfig(
                grafana_url=config["grafana_url"],
                api_key=api_key,
                concurrent_users=config.get("concurrent_users", 10),
                test_duration_seconds=config.get("duration_seconds", 60),
                ramp_up_seconds=config.get("ramp_up_seconds", 5)
            )
            
            tester = GrafanaLoadTester(test_config)
            tester.run_load_test()
            
            # Results are stored within the tester object
            return {
                "status": "completed",
                "summary": {
                    "concurrent_users": config.get("concurrent_users", 10),
                    "duration_seconds": config.get("duration_seconds", 60)
                }
            }
        except Exception as e:
            logger.error(f"Error running load tests: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_security_tests(self) -> Dict:
        """Run security compliance checks"""
        if not self.config.get("security_tests", {}).get("enabled", False):
            logger.info("Security tests disabled, skipping")
            return {"status": "skipped"}
        
        logger.info("Running security compliance checks")
        
        try:
            from security import run_basic_security_scan, verify_resource_tags
            
            config = self.config["security_tests"]
            region = config.get("region", "us-gov-west-1")
            endpoint_url = config.get("endpoint_url")
            
            # Run basic security scans
            resource_types = ["eks", "vpc", "s3", "prometheus", "grafana"]
            scan_results = {}
            
            for resource_type in resource_types:
                resource_id = f"test-{resource_type}"
                scan_results[resource_type] = run_basic_security_scan(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    region=region,
                    endpoint_url=endpoint_url
                )
            
            # Verify tags
            required_tags = ["Environment", "Owner", "Project", "Service"]
            tag_results = {}
            
            for resource_type in resource_types:
                resource_id = f"test-{resource_type}"
                tag_results[resource_type] = verify_resource_tags(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    required_tags=required_tags,
                    region=region,
                    endpoint_url=endpoint_url
                )
            
            return {
                "status": "completed",
                "scan_results": scan_results,
                "tag_results": tag_results
            }
        except Exception as e:
            logger.error(f"Error running security tests: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_infrastructure_tests(self) -> Dict:
        """Run infrastructure validation tests"""
        if not self.config.get("infrastructure_tests", {}).get("enabled", False):
            logger.info("Infrastructure tests disabled, skipping")
            return {"status": "skipped"}
        
        logger.info("Running infrastructure validation tests")
        
        try:
            from tests.eks_integration_test import EksIntegrationTester
            
            config = self.config["infrastructure_tests"]
            
            tester = EksIntegrationTester(
                cluster_name=config["cluster_name"],
                region=config.get("region", "us-gov-west-1")
            )
            
            logger.info("Running all validation tests...")
            results = tester.run_all_tests()
            
            # Export results if configured
            output_file = config.get("output_file", f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            return {
                "status": "completed",
                "all_passed": results["all_passed"],
                "test_count": len(results["tests"]),
                "passed_count": sum(1 for r in results["tests"].values() if r["success"]),
                "output_file": output_file
            }
        except Exception as e:
            logger.error(f"Error running infrastructure tests: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_metric_generation(self) -> Dict:
        """Generate test metrics for Prometheus"""
        if not self.config.get("metric_generation", {}).get("enabled", False):
            logger.info("Metric generation disabled, skipping")
            return {"status": "skipped"}
        
        logger.info("Generating test metrics for Prometheus")
        
        try:
            from data_generator.prometheus_metrics import PrometheusMetricsGenerator
            
            config = self.config["metric_generation"]
            
            generator = PrometheusMetricsGenerator(
                push_gateway_url=config.get("push_gateway_url"),
                simulate_app_name=config.get("app_name", "obs-test-app")
            )
            
            # Generate metrics for the specified duration
            duration_seconds = config.get("duration_seconds", 30)
            update_interval = config.get("update_interval", 1.0)
            
            logger.info(f"Generating metrics for {duration_seconds} seconds")
            generator.generate_metrics_for_duration(
                duration_seconds=duration_seconds,
                update_interval=update_interval
            )
            
            # Export sample metrics if configured
            output_file = config.get("output_file", "sample_metrics.json")
            generator.export_sample_metrics_json(output_file)
            
            # Generate historic data if configured
            if config.get("generate_historic", False):
                historic_file = config.get("historic_file", "historic_metrics.json")
                days_back = config.get("days_back", 30)
                data_points_per_day = config.get("data_points_per_day", 24)
                
                generator.generate_historic_data(
                    days_back=days_back,
                    data_points_per_day=data_points_per_day,
                    output_file=historic_file
                )
                
                logger.info(f"Generated historic data for {days_back} days in {historic_file}")
            
            return {
                "status": "completed",
                "duration_seconds": duration_seconds,
                "output_file": output_file
            }
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """Run all configured tests"""
        self.start_time = time.time()
        logger.info("Starting test run")
        
        # Run the different test types
        self.results["api_tests"] = self.run_api_tests()
        self.results["load_tests"] = self.run_load_tests()
        self.results["security_tests"] = self.run_security_tests()
        self.results["infrastructure_tests"] = self.run_infrastructure_tests()
        self.results["metric_generation"] = self.run_metric_generation()
        
        self.end_time = time.time()
        duration_seconds = self.end_time - self.start_time
        
        # Generate summary
        summary = {
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "duration_seconds": duration_seconds,
            "test_types": {
                "api_tests": self.results["api_tests"]["status"],
                "load_tests": self.results["load_tests"]["status"],
                "security_tests": self.results["security_tests"]["status"],
                "infrastructure_tests": self.results["infrastructure_tests"]["status"],
                "metric_generation": self.results["metric_generation"]["status"]
            }
        }
        
        logger.info(f"Test run completed in {duration_seconds:.2f} seconds")
        
        # Generate report
        self.generate_report(summary)
        
        return {
            "summary": summary,
            "results": self.results
        }
    
    def generate_report(self, summary: Dict) -> None:
        """Generate a test report"""
        report_file = self.config.get("output", {}).get("report_file", "test_report.json")
        report_format = self.config.get("output", {}).get("report_format", "json")
        
        report = {
            "summary": summary,
            "results": self.results
        }
        
        if report_format == "json":
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
        else:
            logger.warning(f"Unsupported report format: {report_format}")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        logger.info(f"Test report generated: {report_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Observability Infrastructure Test Runner")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    args = parser.parse_args()
    
    runner = TestRunner(config_file=args.config)
    results = runner.run_all_tests()
    
    sys.exit(0 if all(v["status"] in ["completed", "skipped"] for v in results["results"].values()) else 1)