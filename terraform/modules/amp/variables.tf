variable "name" {
  description = "Name to be used for the Amazon Managed Prometheus workspace"
  type        = string
}

variable "workspace_alias" {
  description = "Alias for the Amazon Managed Prometheus workspace"
  type        = string
}

variable "retention_in_days" {
  description = "Number of days to retain data in the workspace"
  type        = number
  default     = 30
}

variable "service_role_arn" {
  description = "ARN of the IAM role for Amazon Managed Prometheus"
  type        = string
}