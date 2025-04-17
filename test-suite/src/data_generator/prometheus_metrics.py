import random
import time
import uuid
import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    push_to_gateway, CollectorRegistry
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MetricDefinition:
    """Definition of a Prometheus metric"""
    name: str  
    type: str  # counter, gauge, histogram, summary
    help_text: str
    labels: List[str] = None
    buckets: List[float] = None  # For histograms
    
    def __post_init__(self):
        self.labels = self.labels or []
        self.buckets = self.buckets or [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]

class PrometheusMetricsGenerator:
    """Generates realistic Prometheus metrics for testing"""
    
    def __init__(self, 
                push_gateway_url: Optional[str] = None,
                simulate_app_name: str = "mock-obs-app"):
        self.registry = CollectorRegistry()
        self.push_gateway_url = push_gateway_url
        self.simulate_app_name = simulate_app_name
        self.metrics = {}
        self.metrics_definitions = []
        
        # Set up common financial application metrics
        self.setup_common_metrics()
    
    def setup_common_metrics(self):
        """Set up common metrics for a financial application"""
        self.add_metric_definition(
            MetricDefinition(
                name="http_requests_total",
                type="counter",
                help_text="Total number of HTTP requests",
                labels=["method", "endpoint", "status"]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="http_request_duration_seconds",
                type="histogram",
                help_text="HTTP request latency in seconds",
                labels=["method", "endpoint"],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="payment_transaction_total",
                type="counter",
                help_text="Total number of payment transactions",
                labels=["status", "payment_type", "region"]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="payment_transaction_amount",
                type="histogram",
                help_text="Payment transaction amounts",
                labels=["payment_type", "currency"],
                buckets=[10, 50, 100, 500, 1000, 5000, 10000, 50000]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="system_memory_usage_bytes",
                type="gauge",
                help_text="Current memory usage",
                labels=["instance", "component"]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="system_cpu_usage_percent",
                type="gauge",
                help_text="Current CPU usage percentage",
                labels=["instance", "component", "mode"]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="database_connections",
                type="gauge",
                help_text="Current number of database connections",
                labels=["database", "instance"]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="database_query_duration_seconds",
                type="histogram",
                help_text="Database query duration in seconds",
                labels=["database", "query_type"],
                buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
            )
        )
        
        self.add_metric_definition(
            MetricDefinition(
                name="api_rate_limit_remaining",
                type="gauge",
                help_text="Remaining API rate limit",
                labels=["api", "endpoint"]
            )
        )
        
        # Initialize all metrics based on definitions
        self.initialize_metrics()
    
    def add_metric_definition(self, definition: MetricDefinition):
        """Add a new metric definition"""
        self.metrics_definitions.append(definition)
    
    def initialize_metrics(self):
        """Initialize all metrics based on their definitions"""
        for definition in self.metrics_definitions:
            if definition.type == "counter":
                self.metrics[definition.name] = Counter(
                    definition.name,
                    definition.help_text,
                    definition.labels,
                    registry=self.registry
                )
            elif definition.type == "gauge":
                self.metrics[definition.name] = Gauge(
                    definition.name,
                    definition.help_text,
                    definition.labels,
                    registry=self.registry
                )
            elif definition.type == "histogram":
                self.metrics[definition.name] = Histogram(
                    definition.name,
                    definition.help_text,
                    definition.labels,
                    buckets=definition.buckets,
                    registry=self.registry
                )
            elif definition.type == "summary":
                self.metrics[definition.name] = Summary(
                    definition.name,
                    definition.help_text,
                    definition.labels,
                    registry=self.registry
                )
            else:
                logger.warning(f"Unknown metric type: {definition.type}")
    
    def generate_label_values(self, metric_name: str) -> Dict[str, str]:
        """Generate realistic values for metric labels"""
        for definition in self.metrics_definitions:
            if definition.name == metric_name:
                labels = {}
                
                if "http_requests" in metric_name:
                    labels["method"] = random.choice(["GET", "POST", "PUT", "DELETE"])
                    labels["endpoint"] = random.choice([
                        "/api/v1/payments", 
                        "/api/v1/accounts",
                        "/api/v1/transfers",
                        "/api/v1/users",
                        "/health",
                        "/metrics"
                    ])
                    if "status" in definition.labels:
                        # Mostly successful status codes with occasional errors
                        status_choices = [200] * 80 + [400] * 10 + [500] * 5 + [403] * 3 + [429] * 2
                        labels["status"] = str(random.choice(status_choices))
                
                if "payment_transaction" in metric_name:
                    if "status" in definition.labels:
                        labels["status"] = random.choice([
                            "success", "pending", "failed", "cancelled"
                        ])
                    if "payment_type" in definition.labels:
                        labels["payment_type"] = random.choice([
                            "credit_card", "debit_card", "bank_transfer", "wire", "ach"
                        ])
                    if "region" in definition.labels:
                        labels["region"] = random.choice([
                            "us-east", "us-west", "eu-central", "ap-southeast"
                        ])
                    if "currency" in definition.labels:
                        labels["currency"] = random.choice([
                            "USD", "EUR", "GBP", "JPY", "CAD"
                        ])
                
                if "system_" in metric_name:
                    if "instance" in definition.labels:
                        labels["instance"] = f"node-{random.randint(1, 10)}.example.com:9100"
                    if "component" in definition.labels:
                        labels["component"] = random.choice([
                            "app", "database", "cache", "worker"
                        ])
                    if "mode" in definition.labels:
                        labels["mode"] = random.choice([
                            "user", "system", "idle", "iowait"
                        ])
                
                if "database_" in metric_name:
                    if "database" in definition.labels:
                        labels["database"] = random.choice([
                            "postgres", "mongodb", "redis", "mysql"
                        ])
                    if "instance" in definition.labels:
                        labels["instance"] = f"db-{random.randint(1, 5)}.example.com"
                    if "query_type" in definition.labels:
                        labels["query_type"] = random.choice([
                            "select", "insert", "update", "delete", "transaction"
                        ])
                
                if "api_rate_limit" in metric_name:
                    if "api" in definition.labels:
                        labels["api"] = random.choice([
                            "payment_gateway", "fraud_detection", "customer_service"
                        ])
                    if "endpoint" in definition.labels:
                        labels["endpoint"] = random.choice([
                            "/auth", "/payments", "/accounts", "/transfers"
                        ])
                
                return labels
        
        return {}
    
    def generate_metric_value(self, metric_name: str) -> Union[float, int]:
        """Generate a realistic value for a given metric"""
        
        # HTTP request related values
        if metric_name == "http_requests_total":
            return random.randint(1, 5)  # 1-5 requests per update
        
        if metric_name == "http_request_duration_seconds":
            # Most requests are fast, but some are slow
            fast = random.uniform(0.01, 0.2)  # 10-200ms
            slow = random.uniform(0.5, 3.0)   # 500ms-3s
            very_slow = random.uniform(5.0, 10.0)  # 5-10s
            
            # 80% fast, 15% slow, 5% very slow
            return random.choices(
                [fast, slow, very_slow],
                weights=[80, 15, 5]
            )[0]
        
        # Payment related values
        if metric_name == "payment_transaction_total":
            return random.randint(1, 10)  # 1-10 transactions per update
        
        if metric_name == "payment_transaction_amount":
            # Different realistic transaction amounts
            small = random.uniform(10, 100)     # $10-100
            medium = random.uniform(100, 1000)  # $100-1000
            large = random.uniform(1000, 10000) # $1000-10000
            
            return random.choices(
                [small, medium, large],
                weights=[70, 25, 5]
            )[0]
        
        # System metric values
        if metric_name == "system_memory_usage_bytes":
            # Values in MB converted to bytes
            return random.uniform(100, 4096) * 1024 * 1024
        
        if metric_name == "system_cpu_usage_percent":
            # Normal CPU usage with occasional spikes
            normal = random.uniform(5, 35) 
            high = random.uniform(50, 95)
            
            return random.choices(
                [normal, high],
                weights=[90, 10]
            )[0]
        
        # Database metrics
        if metric_name == "database_connections":
            return random.randint(5, 100)
        
        if metric_name == "database_query_duration_seconds":
            # Most queries are fast
            return random.uniform(0.001, 0.5)
        
        # API rate limit (decreasing over time)
        if metric_name == "api_rate_limit_remaining":
            return max(0, 1000 - random.randint(0, 100))
        
        # Default fallback for other metrics
        if "counter" in metric_name:
            return random.randint(1, 10)
        elif "gauge" in metric_name:
            return random.uniform(0, 100)
        elif "histogram" in metric_name or "duration" in metric_name:
            return random.uniform(0.01, 10.0)
        else:
            return random.uniform(0, 1000)
    
    def update_all_metrics(self):
        """Update all metrics with realistic values"""
        for metric_name, metric in self.metrics.items():
            for definition in self.metrics_definitions:
                if definition.name == metric_name:
                    # Generate between 1-5 different label combinations per metric
                    for _ in range(random.randint(1, 5)):
                        labels = self.generate_label_values(metric_name)
                        value = self.generate_metric_value(metric_name)
                        
                        if definition.type == "counter":
                            metric.labels(**labels).inc(value)
                        elif definition.type == "gauge":
                            # 50% chance of increasing, 50% chance of decreasing
                            if random.random() > 0.5:
                                metric.labels(**labels).inc(value * 0.1)
                            else:
                                metric.labels(**labels).dec(value * 0.1)
                        elif definition.type == "histogram" or definition.type == "summary":
                            metric.labels(**labels).observe(value)
    
    def generate_metrics_for_duration(self, duration_seconds: int, update_interval: float = 1.0):
        """Generate metrics for a specified duration"""
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            self.update_all_metrics()
            
            if self.push_gateway_url:
                try:
                    push_to_gateway(
                        self.push_gateway_url, 
                        job=self.simulate_app_name,
                        registry=self.registry
                    )
                    logger.info(f"Pushed metrics to gateway: {self.push_gateway_url}")
                except Exception as e:
                    logger.error(f"Failed to push metrics to gateway: {e}")
            
            time.sleep(update_interval)
    
    def export_sample_metrics_json(self, filename: str):
        """Export sample metrics as JSON for review"""
        sample_data = {}
        
        for metric_name in self.metrics:
            # Generate sample data points
            sample_data[metric_name] = []
            
            # Generate 5 sample data points per metric
            for _ in range(5):
                labels = self.generate_label_values(metric_name)
                value = self.generate_metric_value(metric_name)
                
                sample_data[metric_name].append({
                    "labels": labels,
                    "value": value,
                    "timestamp": datetime.now().isoformat()
                })
        
        with open(filename, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        logger.info(f"Exported sample metrics to {filename}")

    def generate_historic_data(self, 
                              days_back: int = 30, 
                              data_points_per_day: int = 24,
                              output_file: Optional[str] = None) -> List[Dict]:
        """Generate historic data for testing visualization"""
        historic_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Create timestamps for data points
        timestamps = []
        current_date = start_date
        interval = timedelta(days=1) / data_points_per_day
        
        while current_date <= end_date:
            timestamps.append(current_date)
            current_date += interval
        
        # Generate data for each metric
        for metric_name in self.metrics:
            # Create several series with different label combinations
            for series_idx in range(random.randint(2, 5)):
                labels = self.generate_label_values(metric_name)
                series_data = []
                
                # Create a recognizable pattern
                pattern_type = random.choice(["steady", "growing", "cyclic", "spiky"])
                base_value = self.generate_metric_value(metric_name)
                
                for idx, ts in enumerate(timestamps):
                    if pattern_type == "steady":
                        # Steady with small variations
                        value = base_value * random.uniform(0.9, 1.1)
                    elif pattern_type == "growing":
                        # Growing trend
                        growth_factor = 1 + (idx / len(timestamps))
                        value = base_value * growth_factor * random.uniform(0.95, 1.05)
                    elif pattern_type == "cyclic":
                        # Cyclic pattern (like day/night cycle)
                        hour_of_day = ts.hour
                        day_factor = 0.5 + 0.5 * abs(math.sin(hour_of_day * math.pi / 12))
                        value = base_value * day_factor * random.uniform(0.9, 1.1)
                    elif pattern_type == "spiky":
                        # Mostly normal with occasional spikes
                        is_spike = random.random() < 0.05  # 5% chance of spike
                        value = base_value * (5 if is_spike else 1) * random.uniform(0.9, 1.1)
                    
                    series_data.append({
                        "timestamp": ts.isoformat(),
                        "value": value,
                    })
                
                # Add the series to historic data
                historic_data.append({
                    "metric": metric_name,
                    "labels": labels,
                    "pattern": pattern_type,
                    "data": series_data
                })
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(historic_data, f, indent=2)
            logger.info(f"Exported historic data to {output_file}")
        
        return historic_data