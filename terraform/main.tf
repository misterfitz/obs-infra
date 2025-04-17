module "vpc" {
  source = "./modules/vpc"

  name                 = var.name
  cidr                 = var.vpc_cidr
  azs                  = var.azs
  private_subnets      = var.private_subnets
  public_subnets       = var.public_subnets
  enable_nat_gateway   = true
  single_nat_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  # EKS specific tags for subnet discovery
  private_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "shared"
    "kubernetes.io/role/internal-elb"   = 1
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "shared"
    "kubernetes.io/role/elb"            = 1
  }
}

module "iam" {
  source = "./modules/iam"

  name                       = var.name
  eks_cluster_service_role   = var.eks_cluster_service_role
  eks_node_role              = var.eks_node_role
  prometheus_service_role    = var.prometheus_service_role
  grafana_service_role       = var.grafana_service_role
}

module "eks" {
  source = "./modules/eks"

  cluster_name                   = var.name
  cluster_version                = var.cluster_version
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_service_role_arn       = module.iam.eks_cluster_role_arn
  eks_managed_node_groups        = var.eks_managed_node_groups
  node_security_group_additional_rules = var.node_security_group_additional_rules
}

module "amp" {
  source = "./modules/amp"

  name                = "${var.name}-prometheus"
  workspace_alias     = var.prometheus_workspace_alias
  retention_in_days   = var.prometheus_retention_in_days
  service_role_arn    = module.iam.prometheus_role_arn
  depends_on          = [module.eks]
}

module "amg" {
  source = "./modules/amg"

  name                = "${var.name}-grafana"
  workspace_name      = var.grafana_workspace_name
  workspace_role_arn  = module.iam.grafana_role_arn
  data_sources        = ["PROMETHEUS"]
  authentication_type = "AWS_SSO"
  permission_type     = "SERVICE_MANAGED"
  prometheus_workspace_id = module.amp.workspace_id
  depends_on          = [module.amp]
}