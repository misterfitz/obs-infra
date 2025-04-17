# src/tests/eks_integration_test.py
import boto3
import kubernetes
import requests
import logging
import time
import json
from kubernetes import client, config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EksIntegrationTester:
    """Tests the entire EKS stack including Prometheus integration"""
    
    def __init__(self, 
                cluster_name: str,
                region: str = "us-gov-west-1",
                namespace: str = "monitoring"):
        self.cluster_name = cluster_name
        self.region = region
        self.namespace = namespace
        self.test_results = {}
        
        # Initialize AWS clients
        self.eks_client = boto3.client('eks', region_name=region)
        self.amp_client = boto3.client('amp', region_name=region)
        self.amg_client = boto3.client('grafana', region_name=region)
        
        # Get cluster details and configure kubectl
        self._configure_kubernetes()
    
    def _configure_kubernetes(self):
        """Configure kubernetes client from EKS cluster"""
        logger.info(f"Configuring Kubernetes client for {self.cluster_name}")
        
        try:
            cluster_info = self.eks_client.describe_cluster(name=self.cluster_name)
            cluster = cluster_info['cluster']
            
            # Configure kubectl
            cmd = f"aws eks update-kubeconfig --name {self.cluster_name} --region {self.region}"
            logger.info(f"Running: {cmd}")
            import subprocess
            subprocess.run(cmd, shell=True, check=True)
            
            # Load kube config
            config.load_kube_config()
            self.k8s_api = client.CoreV1Api()
            self.k8s_apps_api = client.AppsV1Api()
            
            logger.info("Kubernetes client configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to configure Kubernetes client: {e}")
            return False
    
    def test_eks_cluster_health(self):
        """Test if EKS cluster is healthy"""
        logger.info(f"Testing EKS cluster health: {self.cluster_name}")
        
        try:
            # Check cluster status
            cluster_info = self.eks_client.describe_cluster(name=self.cluster_name)
            cluster_status = cluster_info['cluster']['status']
            
            # Check nodes
            nodes = self.k8s_api.list_node()
            ready_nodes = 0
            
            for node in nodes.items:
                for condition in node.status.conditions:
                    if condition.type == "Ready" and condition.status == "True":
                        ready_nodes += 1
            
            result = {
                "cluster_status": cluster_status,
                "total_nodes": len(nodes.items),
                "ready_nodes": ready_nodes,
                "healthy": cluster_status == "ACTIVE" and ready_nodes == len(nodes.items)
            }
            
            self.test_results["eks_cluster_health"] = result
            logger.info(f"EKS Cluster Health: {result}")
            
            return result["healthy"]
        except Exception as e:
            logger.error(f"Error testing EKS cluster health: {e}")
            self.test_results["eks_cluster_health"] = {
                "error": str(e),
                "healthy": False
            }
            return False
    
    def test_prometheus_integration(self):
        """Test Prometheus integration with EKS"""
        logger.info("Testing Prometheus integration")
        
        try:
            # Check if prometheus namespace exists
            try:
                ns = self.k8s_api.read_namespace(name=self.namespace)
                logger.info(f"Namespace {self.namespace} exists")
            except kubernetes.client.exceptions.ApiException:
                logger.error(f"Namespace {self.namespace} does not exist")
                return False
            
            # Check if prometheus operator pods are running
            pods = self.k8s_api.list_namespaced_pod(namespace=self.namespace)
            prometheus_pods = [p for p in pods.items if "prometheus" in p.metadata.name]
            
            if not prometheus_pods:
                logger.error("No Prometheus pods found")
                self.test_results["prometheus_integration"] = {
                    "status": "No pods found",
                    "healthy": False
                }
                return False
            
            # Check if pods are running
            all_running = all(p.status.phase == "Running" for p in prometheus_pods)
            
            # Check if prometheus service is available
            try:
                svc = self.k8s_api.read_namespaced_service(name="prometheus-server", namespace=self.namespace)
                prometheus_service_found = True
            except kubernetes.client.exceptions.ApiException:
                prometheus_service_found = False
            
            result = {
                "prometheus_pods_found": len(prometheus_pods) > 0,
                "all_pods_running": all_running,
                "prometheus_service_found": prometheus_service_found,
                "healthy": len(prometheus_pods) > 0 and all_running and prometheus_service_found
            }
            
            self.test_results["prometheus_integration"] = result
            logger.info(f"Prometheus Integration: {result}")
            
            return result["healthy"]
        except Exception as e:
            logger.error(f"Error testing Prometheus integration: {e}")
            self.test_results["prometheus_integration"] = {
                "error": str(e),
                "healthy": False
            }
            return False
    
    def test_amp_workspace(self):
        """Test AWS Managed Prometheus workspace"""
        logger.info("Testing AWS Managed Prometheus workspace")
        
        try:
            # List workspaces
            workspaces = self.amp_client.list_workspaces()
            
            if not workspaces.get('workspaces'):
                logger.error("No Prometheus workspaces found")
                self.test_results["amp_workspace"] = {
                    "status": "No workspaces found",
                    "healthy": False
                }
                return False
            
            # Find workspace with the proper prefix
            workspace = None
            for ws in workspaces['workspaces']:
                if ws['alias'].startswith(self.cluster_name):
                    workspace = ws
                    break
            
            if not workspace:
                logger.error(f"No workspace found for {self.cluster_name}")
                self.test_results["amp_workspace"] = {
                    "status": "No matching workspace",
                    "healthy": False
                }
                return False
            
            # Check workspace status
            workspace_id = workspace['workspaceId']
            workspace_details = self.amp_client.describe_workspace(workspaceId=workspace_id)
            
            status = workspace_details['workspace']['status']['statusCode']
            
            result = {
                "workspace_id": workspace_id,
                "status": status,
                "healthy": status == "ACTIVE"
            }
            
            self.test_results["amp_workspace"] = result
            logger.info(f"AMP Workspace: {result}")
            
            return result["healthy"]
        except Exception as e:
            logger.error(f"Error testing AMP workspace: {e}")
            self.test_results["amp_workspace"] = {
                "error": str(e),
                "healthy": False
            }
            return False
    
    def test_grafana_workspace(self):
        """Test AWS Managed Grafana workspace"""
        logger.info("Testing AWS Managed Grafana workspace")
        
        try:
            # List workspaces
            workspaces = self.amg_client.list_workspaces()
            
            if not workspaces.get('workspaces'):
                logger.error("No Grafana workspaces found")
                self.test_results["grafana_workspace"] = {
                    "status": "No workspaces found",
                    "healthy": False
                }
                return False
            
            # Find workspace with the proper prefix
            workspace = None
            for ws in workspaces['workspaces']:
                if ws['name'].startswith(self.cluster_name):
                    workspace = ws
                    break
            
            if not workspace:
                logger.error(f"No workspace found for {self.cluster_name}")
                self.test_results["grafana_workspace"] = {
                    "status": "No matching workspace",
                    "healthy": False
                }
                return False
            
            # Check workspace status
            workspace_id = workspace['id']
            
            result = {
                "workspace_id": workspace_id,
                "status": workspace['status'],
                "endpoint": workspace.get('endpoint', ''),
                "healthy": workspace['status'] == "ACTIVE"
            }
            
            self.test_results["grafana_workspace"] = result
            logger.info(f"AMG Workspace: {result}")
            
            return result["healthy"]
        except Exception as e:
            logger.error(f"Error testing AMG workspace: {e}")
            self.test_results["grafana_workspace"] = {
                "error": str(e),
                "healthy": False
            }
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("Starting all integration tests")
        
        tests = [
            self.test_eks_cluster_health,
            self.test_prometheus_integration,
            self.test_amp_workspace,
            self.test_grafana_workspace
        ]
        
        results = {}
        
        for test in tests:
            test_name = test.__name__
            logger.info(f"Running test: {test_name}")
            start_time = time.time()
            success = test()
            end_time = time.time()
            
            results[test_name] = {
                "success": success,
                "duration_ms": (end_time - start_time) * 1000
            }
        
        # Overall result
        all_passed = all(r["success"] for r in results.values())
        
        logger.info(f"All tests completed. Overall status: {'PASSED' if all_passed else 'FAILED'}")
        
        return {
            "all_passed": all_passed,
            "tests": results,
            "details": self.test_results
        }
    
    def export_results(self, filename):
        """Export test results to a file"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Results exported to {filename}")