output "workspace_id" {
  description = "ID of the Amazon Managed Prometheus workspace"
  value       = aws_prometheus_workspace.this.id
}

output "workspace_arn" {
  description = "ARN of the Amazon Managed Prometheus workspace"
  value       = aws_prometheus_workspace.this.arn
}

output "workspace_endpoint" {
  description = "Endpoint of the Amazon Managed Prometheus workspace"
  value       = aws_prometheus_workspace.this.prometheus_endpoint
}

output "workspace_alias" {
  description = "Alias of the Amazon Managed Prometheus workspace"
  value       = aws_prometheus_workspace.this.alias
}