output "eks_cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_arn" {
  description = "ARN of the EKS node IAM role"
  value       = aws_iam_role.eks_node_role.arn
}

output "prometheus_role_arn" {
  description = "ARN of the Prometheus IAM role"
  value       = aws_iam_role.prometheus.arn
}

output "grafana_role_arn" {
  description = "ARN of the Grafana IAM role"
  value       = aws_iam_role.grafana.arn
}