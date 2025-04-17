variable "name" {
  description = "Name to be used for the Amazon Managed Grafana workspace"
  type        = string
}

variable "workspace_name" {
  description = "Name for the Amazon Managed Grafana workspace"
  type        = string
}

variable "workspace_role_arn" {
  description = "ARN of the IAM role for Amazon Managed Grafana"
  type        = string
}

variable "data_sources" {
  description = "List of data sources for the workspace"
  type        = list(string)
  default     = ["PROMETHEUS"]
}

variable "authentication_type" {
  description = "Authentication type for the workspace"
  type        = string
  default     = "AWS_SSO"
}

variable "permission_type" {
  description = "Permission type for the workspace"
  type        = string
  default     = "SERVICE_MANAGED"
}

variable "admin_user_ids" {
  description = "List of user IDs to assign the admin role"
  type        = list(string)
  default     = []
}

variable "admin_group_ids" {
  description = "List of group IDs to assign the admin role"
  type        = list(string)
  default     = []
}

variable "prometheus_workspace_id" {
  description = "ID of the Amazon Managed Prometheus workspace to connect"
  type        = string
  default     = ""
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-gov-west-1"
}
