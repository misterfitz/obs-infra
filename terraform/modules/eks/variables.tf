variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version to use for the EKS cluster"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where the cluster will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the EKS cluster"
  type        = list(string)
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to the cluster API endpoint"
  type        = bool
  default     = false
}

variable "cluster_service_role_arn" {
  description = "ARN of the IAM role that provides permissions for the Kubernetes control plane"
  type        = string
}

variable "node_role_arn" {
  description = "ARN of the IAM role for EKS node groups"
  type        = string
  default     = ""
}

variable "eks_managed_node_groups" {
  description = "Map of EKS managed node group definitions"
  type        = map(any)
  default     = {}
}

variable "node_security_group_additional_rules" {
  description = "Additional security group rules for EKS nodes"
  type        = map(any)
  default     = {}
}

variable "lb_controller_role_arn" {
  description = "ARN of the IAM role for AWS Load Balancer Controller"
  type        = string
  default     = ""
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-gov-west-1"
}

variable "amp_workspace_endpoint" {
  description = "AWS Managed Prometheus workspace endpoint"
  type        = string
  default     = ""
}