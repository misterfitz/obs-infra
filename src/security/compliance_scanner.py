# src/security/compliance_scanner.py
import boto3
import json
import logging
import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    """Definition of a compliance rule"""
    id: str
    title: str
    description: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category: str  # 'SECURITY', 'OPERATIONS', 'PERFORMANCE', 'COST'
    service: str   # 'EKS', 'IAM', 'VPC', etc.
    check_function: str  # Name of the function to call for this check

@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    rule_id: str
    status: str  # 'PASS', 'FAIL', 'WARNING', 'NOT_APPLICABLE'
    resource_id: str
    details: str
    remediation: str

class SecurityComplianceScanner:
    """Scans AWS infrastructure for security compliance"""
    
    def __init__(self, region: str = "us-gov-west-1"):
        self.region = region
        self.rules = []
        self.results = []
        
        # Initialize AWS clients
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.eks_client = boto3.client('eks', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudtrail_client = boto3.client('cloudtrail', region_name=region)
        self.config_client = boto3.client('config', region_name=region)
        
        # Load default rules
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default compliance rules"""
        self.rules = [
            ComplianceRule(
                id="SEC-IAM-001",
                title="IAM Root Account MFA",
                description="Checks if the root account has MFA enabled",
                severity="CRITICAL",
                category="SECURITY",
                service="IAM",
                check_function="check_root_mfa"
            ),
            ComplianceRule(
                id="SEC-IAM-002",
                title="IAM Access Keys Rotation",
                description="Checks if IAM access keys are rotated within 90 days",
                severity="HIGH",
                category="SECURITY",
                service="IAM",
                check_function="check_access_key_rotation"
            ),
            ComplianceRule(
                id="SEC-VPC-001",
                title="Default Security Group Restricts All Traffic",
                description="Checks if default security groups restrict all inbound and outbound traffic",
                severity="HIGH",
                category="SECURITY",
                service="VPC",
                check_function="check_default_security_groups"
            ),
            ComplianceRule(
                id="SEC-EKS-001",
                title="EKS Control Plane Logging Enabled",
                description="Checks if EKS control plane logging is enabled",
                severity="MEDIUM",
                category="SECURITY",
                service="EKS",
                check_function="check_eks_logging"
            ),
            ComplianceRule(
                id="SEC-EKS-002",
                title="EKS Cluster Private Endpoint",
                description="Checks if EKS cluster has private endpoint enabled",
                severity="HIGH",
                category="SECURITY",
                service="EKS",
                check_function="check_eks_private_endpoint"
            ),
            ComplianceRule(
                id="SEC-S3-001",
                title="S3 Buckets Block Public Access",
                description="Checks if S3 buckets block public access",
                severity="CRITICAL",
                category="SECURITY",
                service="S3",
                check_function="check_s3_public_access"
            ),
            ComplianceRule(
                id="SEC-S3-002",
                title="S3 Buckets Encrypted",
                description="Checks if S3 buckets are encrypted",
                severity="HIGH",
                category="SECURITY",
                service="S3",
                check_function="check_s3_encryption"
            ),
            ComplianceRule(
                id="SEC-AUDIT-001",
                title="CloudTrail Enabled",
                description="Checks if CloudTrail is enabled",
                severity="CRITICAL",
                category="SECURITY",
                service="CLOUDTRAIL",
                check_function="check_cloudtrail_enabled"
            ),
            # Financial industry specific rules
            ComplianceRule(
                id="FIN-EKS-001",
                title="EKS Worker Node Encryption",
                description="Checks if EKS worker nodes have encryption enabled",
                severity="HIGH",
                category="SECURITY",
                service="EKS",
                check_function="check_eks_node_encryption"
            ),
            ComplianceRule(
                id="FIN-NET-001",
                title="VPC Flow Logs Enabled",
                description="Checks if VPC flow logs are enabled for audit trails",
                severity="HIGH",
                category="SECURITY",
                service="VPC",
                check_function="check_vpc_flow_logs"
            ),
            ComplianceRule(
                id="FIN-TAG-001",
                title="Required Tags Present",
                description="Checks if required financial compliance tags are present",
                severity="MEDIUM",
                category="OPERATIONS",
                service="GENERAL",
                check_function="check_required_tags"
            )
        ]
    
    def check_root_mfa(self) -> List[ComplianceResult]:
        """Check if root account has MFA enabled"""
        try:
            response = self.iam_client.get_account_summary()
            if response['SummaryMap'].get('AccountMFAEnabled', 0) == 1:
                return [ComplianceResult(
                    rule_id="SEC-IAM-001",
                    status="PASS",
                    resource_id="root",
                    details="Root account has MFA enabled",
                    remediation=""
                )]
            else:
                return [ComplianceResult(
                    rule_id="SEC-IAM-001",
                    status="FAIL",
                    resource_id="root",
                    details="Root account does not have MFA enabled",
                    remediation="Enable MFA for the root account through the AWS Management Console"
                )]
        except Exception as e:
            logger.error(f"Error checking root MFA: {e}")
            return [ComplianceResult(
                rule_id="SEC-IAM-001",
                status="ERROR",
                resource_id="root",
                details=f"Error checking: {str(e)}",
                remediation=""
            )]
    
    def check_access_key_rotation(self) -> List[ComplianceResult]:
        """Check if IAM access keys are rotated within 90 days"""
        results = []
        try:
            users = self.iam_client.list_users()['Users']
            for user in users:
                username = user['UserName']
                keys = self.iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']
                
                for key in keys:
                    key_id = key['AccessKeyId']
                    create_date = key['CreateDate']
                    
                    # Calculate age in days
                    import datetime
                    now = datetime.datetime.now(create_date.tzinfo)
                    age_days = (now - create_date).days
                    
                    if age_days > 90:
                        results.append(ComplianceResult(
                            rule_id="SEC-IAM-002",
                            status="FAIL",
                            resource_id=f"{username}/{key_id}",
                            details=f"Access key is {age_days} days old (> 90 days)",
                            remediation=f"Rotate access key for user {username}"
                        ))
                    else:
                        results.append(ComplianceResult(
                            rule_id="SEC-IAM-002",
                            status="PASS",
                            resource_id=f"{username}/{key_id}",
                            details=f"Access key is {age_days} days old (< 90 days)",
                            remediation=""
                        ))
            
            return results
        except Exception as e:
            logger.error(f"Error checking access key rotation: {e}")
            return [ComplianceResult(
                rule_id="SEC-IAM-002",
                status="ERROR",
                resource_id="iam_keys",
                details=f"Error checking: {str(e)}",
                remediation=""
            )]
    
    def check_default_security_groups(self) -> List[ComplianceResult]:
        """Check if default security groups restrict all traffic"""
        results = []
        try:
            vpcs = self.ec2_client.describe_vpcs()['Vpcs']
            for vpc in vpcs:
                vpc_id = vpc['VpcId']
                
                # Get default security group
                security_groups = self.ec2_client.describe_security_groups(
                    Filters=[
                        {'Name': 'vpc-id', 'Values': [vpc_id]},
                        {'Name': 'group-name', 'Values': ['default']}
                    ]
                )['SecurityGroups']
                
                if not security_groups:
                    continue
                
                sg = security_groups[0]
                sg_id = sg['GroupId']
                
                inbound_rules = sg['IpPermissions']
                outbound_rules = sg['IpPermissionsEgress']
                
                if inbound_rules:
                    results.append(ComplianceResult(
                        rule_id="SEC-VPC-001",
                        status="FAIL",
                        resource_id=sg_id,
                        details=f"Default security group for VPC {vpc_id} allows inbound traffic",
                        remediation=f"Remove all inbound rules from the default security group"
                    ))
                else:
                    results.append(ComplianceResult(
                        rule_id="SEC-VPC-001",
                        status="PASS",
                        resource_id=sg_id,
                        details=f"Default security group for VPC {vpc_id} restricts inbound traffic",
                        remediation=""
                    ))
                
                # Check if outbound rules only have a single rule to deny all traffic
                if len(outbound_rules) != 0:
                    results.append(ComplianceResult(
                        rule_id="SEC-VPC-001",
                        status="FAIL",
                        resource_id=sg_id,
                        details=f"Default security group for VPC {vpc_id} allows outbound traffic",
                        remediation=f"Remove all outbound rules from the default security group"
                    ))
                else:
                    results.append(ComplianceResult(
                        rule_id="SEC-VPC-001",
                        status="PASS",
                        resource_id=sg_id,
                        details=f"Default security group for VPC {vpc_id} restricts outbound traffic",
                        remediation=""
                    ))
            
            return results
        except Exception as e:
            logger.error(f"Error checking default security groups: {e}")
            return [ComplianceResult(
                rule_id="SEC-VPC-001",
                status="ERROR",
                resource_id="security_groups",
                details=f"Error checking: {str(e)}",
                remediation=""
            )]

    # Add implementations for all the check functions
    # ...
    
    def scan_all(self) -> Dict:
        """Run all compliance checks"""
        all_results = []
        
        for rule in self.rules:
            logger.info(f"Running check: {rule.id} - {rule.title}")
            
            try:
                # Get the check function
                check_func = getattr(self, rule.check_function, None)
                
                if check_func:
                    results = check_func()
                    all_results.extend(results)
                else:
                    logger.warning(f"Check function '{rule.check_function}' not found")
                    all_results.append(ComplianceResult(
                        rule_id=rule.id,
                        status="ERROR",
                        resource_id="N/A",
                        details=f"Check function '{rule.check_function}' not implemented",
                        remediation=""
                    ))
            except Exception as e:
                logger.error(f"Error running check {rule.id}: {e}")
                all_results.append(ComplianceResult(
                    rule_id=rule.id,
                    status="ERROR",
                    resource_id="N/A",
                    details=f"Error running check: {str(e)}",
                    remediation=""
                ))
        
        self.results = all_results
        
        # Generate summary
        summary = {
            "total_checks": len(all_results),
            "passed": sum(1 for r in all_results if r.status == "PASS"),
            "failed": sum(1 for r in all_results if r.status == "FAIL"),
            "warnings": sum(1 for r in all_results if r.status == "WARNING"),
            "errors": sum(1 for r in all_results if r.status == "ERROR"),
            "by_severity": {
                "CRITICAL": {
                    "total": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "CRITICAL"),
                    "failed": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "CRITICAL" and r.status == "FAIL")
                },
                "HIGH": {
                    "total": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "HIGH"),
                    "failed": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "HIGH" and r.status == "FAIL")
                },
                "MEDIUM": {
                    "total": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "MEDIUM"),
                    "failed": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "MEDIUM" and r.status == "FAIL")
                },
                "LOW": {
                    "total": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "LOW"),
                    "failed": sum(1 for r in all_results if self._get_rule_severity(r.rule_id) == "LOW" and r.status == "FAIL")
                }
            }
        }
        
        return {
            "summary": summary,
            "results": [vars(r) for r in all_results]
        }
    
    def _get_rule_severity(self, rule_id: str) -> str:
        """Get the severity of a rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule.severity
        return "UNKNOWN"
    
    def export_results_csv(self, filename: str):
        """Export results to CSV"""
        if not self.results:
            logger.warning("No results to export")
            return
        
        data = []
        for result in self.results:
            # Get rule info
            rule = next((r for r in self.rules if r.id == result.rule_id), None)
            
            if rule:
                data.append({
                    "Rule ID": result.rule_id,
                    "Title": rule.title,
                    "Severity": rule.severity,
                    "Category": rule.category,
                    "Service": rule.service,
                    "Status": result.status,
                    "Resource ID": result.resource_id,
                    "Details": result.details,
                    "Remediation": result.remediation
                })
            else:
                data.append({
                    "Rule ID": result.rule_id,
                    "Title": "Unknown",
                    "Severity": "Unknown",
                    "Category": "Unknown",
                    "Service": "Unknown",
                    "Status": result.status,
                    "Resource ID": result.resource_id,
                    "Details": result.details,
                    "Remediation": result.remediation
                })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        logger.info(f"Results exported to {filename}")
    
    def export_results_html(self, filename: str):
        """Export results to HTML report"""
        if not self.results:
            logger.warning("No results to export")
            return
        
        data = []
        for result in self.results:
            # Get rule info
            rule = next((r for r in self.rules if r.id == result.rule_id), None)
            
            if rule:
                data.append({
                    "Rule ID": result.rule_id,
                    "Title": rule.title,
                    "Severity": rule.severity,
                    "Category": rule.category,
                    "Service": rule.service,
                    "Status": result.status,
                    "Resource ID": result.resource_id,
                    "Details": result.details,
                    "Remediation": result.remediation
                })
            else:
                data.append({
                    "Rule ID": result.rule_id,
                    "Title": "Unknown",
                    "Severity": "Unknown",
                    "Category": "Unknown", 
                    "Service": "Unknown",
                    "Status": result.status,
                    "Resource ID": result.resource_id,
                    "Details": result.details,
                    "Remediation": result.remediation
                })
        
        df = pd.DataFrame(data)
        
        # Generate HTML report
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AWS Security Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #1a5276; }}
                .summary {{ margin-bottom: 20px; }}
                .table-container {{ margin-top: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .PASS {{ background-color: #dff0d8; }}
                .FAIL {{ background-color: #f2dede; }}
                .WARNING {{ background-color: #fcf8e3; }}
                .ERROR {{ background-color: #f5f5f5; }}
                .CRITICAL {{ color: #d9534f; font-weight: bold; }}
                .HIGH {{ color: #f0ad4e; font-weight: bold; }}
                .MEDIUM {{ color: #5bc0de; }}
                .LOW {{ color: #5cb85c; }}
            </style>
        </head>
        <body>
            <h1>AWS Security Compliance Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>
                    <strong>Total Checks:</strong> {len(self.results)}<br>
                    <strong>Passed:</strong> {sum(1 for r in self.results if r.status == "PASS")}<br>
                    <strong>Failed:</strong> {sum(1 for r in self.results if r.status == "FAIL")}<br>
                    <strong>Warnings:</strong> {sum(1 for r in self.results if r.status == "WARNING")}<br>
                    <strong>Errors:</strong> {sum(1 for r in self.results if r.status == "ERROR")}
                </p>
            </div>
            
            <div class="table-container">
                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>Rule ID</th>
                        <th>Title</th>
                        <th>Severity</th>
                        <th>Category</th>
                        <th>Service</th>
                        <th>Status</th>
                        <th>Resource ID</th>
                        <th>Details</th>
                        <th>Remediation</th>
                    </tr>
        """
        
        for index, row in df.iterrows():
            status_class = row["Status"]
            severity_class = row["Severity"]
            
            html += f"""
                    <tr class="{status_class}">