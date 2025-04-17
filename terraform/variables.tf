variable "region" {
  description = "AWS GovCloud region"
  type        = string
  default     = "us-gov-west-1"
}

variable "name" {
  description = "Name to be used on all resources as prefix"
  type        = string
  default     = "observability-stack"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "azs" {
  description = "Availability zones for VPC"
  type        = list(string)
  default     = ["us-gov-west-1a", "us-gov-west-1b", "us-gov-west-1c"]
}

variable "private_subnets" {
  description = "Private subnets for VPC"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnets for VPC"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.26"
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to EKS cluster endpoint"
  type        = bool
  default     = false
}

variable "eks_managed_node_groups" {
  description = "Map of EKS managed node group definitions"
  type        = map(any)
  default     = {
    default = {
      desired_size   = 3
      min_size       = 3
      max_size       = 5
      instance_types = ["m5.large"]
      disk_size      = 50
      capacity_type  = "ON_DEMAND"
    }
  }
}

variable "prometheus_workspace_alias" {
  description = "Alias for AWS Managed Prometheus workspace"
  type        = string
  default     = "obs-amp"
}

variable "prometheus_retention_in_days" {
  description = "Data retention period in days"
  type        = number
  default     = 30
}

variable "grafana_workspace_name" {
  description = "Name for AWS Managed Grafana workspace"
  type        = string
  default     = "obs-amg"
}

variable "node_security_group_additional_rules" {
  type = map(object({
    description = string
    protocol    = string
    from_port   = number
    to_port     = number
    type        = string
    self        = optional(bool)
    cidr_blocks = optional(list(string))
  }))
  default = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    egress_all = {
      description = "Node all egress"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
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