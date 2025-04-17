output "workspace_id" {
  description = "ID of the Amazon Managed Grafana workspace"
  value       = aws_grafana_workspace.this.id
}

output "workspace_arn" {
  description = "ARN of the Amazon Managed Grafana workspace"
  value       = aws_grafana_workspace.this.arn
}

output "workspace_endpoint" {
  description = "Endpoint of the Amazon Managed Grafana workspace"
  value       = aws_grafana_workspace.this.endpoint
}

output "api_key" {
  description = "API key for the Grafana workspace"
  value       = aws_grafana_workspace_api_key.this.key
  sensitive   = true
}