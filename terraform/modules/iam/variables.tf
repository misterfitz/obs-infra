variable "name" {
  description = "Name to be used on all resources as prefix"
  type        = string
}

variable "eks_cluster_service_role" {
  description = "Role name for EKS cluster"
  type        = string
  default     = "eks-cluster-role"
}

variable "eks_node_role" {
  description = "Role name for EKS worker nodes"
  type        = string
  default     = "eks-node-role"
}

variable "prometheus_service_role" {
  description = "Role name for AWS Managed Prometheus"
  type        = string
  default     = "prometheus-service-role"
}

variable "grafana_service_role" {
  description = "Role name for AWS Managed Grafana"
  type        = string
  default     = "grafana-service-role"
}