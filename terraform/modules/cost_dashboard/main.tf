# modules/cost_dashboard/main.tf
resource "aws_cloudwatch_dashboard" "cost_optimization" {
  dashboard_name = "${var.name}-cost-optimization"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.cluster_name, { "stat" = "Average" }]
          ]
          view = "timeSeries"
          stacked = false
          region = var.region
          title = "EKS CPU Utilization"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.cluster_name, { "stat" = "Average" }]
          ]
          view = "timeSeries"
          stacked = false
          region = var.region
          title = "EKS Memory Utilization"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "${var.name}-eks-nodes", { "stat" = "Average" }]
          ]
          view = "timeSeries"
          stacked = false
          region = var.region
          title = "EC2 CPU Utilization"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.name}-db", { "stat" = "Average" }]
          ]
          view = "timeSeries"
          stacked = false
          region = var.region
          title = "RDS CPU Utilization"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/EC2", "NetworkIn", "AutoScalingGroupName", "${var.name}-eks-nodes", { "stat" = "Sum" }],
            ["AWS/EC2", "NetworkOut", "AutoScalingGroupName", "${var.name}-eks-nodes", { "stat" = "Sum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = var.region
          title = "Network Traffic"
          period = 300
        }
      },
      {
        type   = "text"
        x      = 0
        y      = 18
        width  = 24
        height = 2
        properties = {
          markdown = "# Cost Optimization Recommendations\n\n* Consider using Reserved Instances for stable workloads\n* Use Spot Instances for batch processing workloads\n* Right-size instances based on utilization data\n* Enable auto-scaling to match capacity with demand\n* Implement cost allocation tags for better visibility"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_dashboard" "billing_dashboard" {
  dashboard_name = "${var.name}-billing"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "Currency", "USD", { "stat" = "Maximum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = "us-east-1"  # Billing metrics are only available in us-east-1
          title = "Estimated AWS Charges (USD)"
          period = 86400
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonEKS", "Currency", "USD", { "stat" = "Maximum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = "us-east-1"
          title = "EKS Charges"
          period = 86400
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonEC2", "Currency", "USD", { "stat" = "Maximum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = "us-east-1"
          title = "EC2 Charges"
          period = 86400
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonPrometheus", "Currency", "USD", { "stat" = "Maximum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = "us-east-1"
          title = "Amazon Managed Prometheus Charges"
          period = 86400
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonGrafana", "Currency", "USD", { "stat" = "Maximum" }]
          ]
          view = "timeSeries"
          stacked = false
          region = "us-east-1"
          title = "Amazon Managed Grafana Charges"
          period = 86400
        }
      }
    ]
  })
}