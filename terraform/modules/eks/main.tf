resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  role_arn = var.cluster_service_role_arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.cluster_endpoint_public_access
    security_group_ids      = [aws_security_group.cluster.id]
  }

  depends_on = [
    aws_security_group.cluster
  ]
}

resource "aws_security_group" "cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "Cluster security group for EKS"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_eks_node_group" "this" {
  for_each = var.eks_managed_node_groups

  cluster_name    = aws_eks_cluster.this.name
  node_group_name = each.key
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = each.value.desired_size
    min_size     = each.value.min_size
    max_size     = each.value.max_size
  }

  instance_types = each.value.instance_types
  disk_size      = each.value.disk_size
  capacity_type  = each.value.capacity_type

  depends_on = [aws_eks_cluster.this]
}

# Install AWS Load Balancer Controller for ingress
resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.5.3"

  set {
    name  = "clusterName"
    value = aws_eks_cluster.this.name
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.lb_controller_role_arn
  }

  depends_on = [aws_eks_cluster.this]
}

# Install Prometheus stack to connect with AWS Managed Prometheus
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"
  version    = "45.7.1"
  create_namespace = true

  set {
    name  = "prometheus.prometheusSpec.remoteWrite[0].url"
    value = "${var.amp_workspace_endpoint}api/v1/remote_write"
  }

  set {
    name  = "prometheus.prometheusSpec.remoteWrite[0].sigv4.region"
    value = var.region
  }

  set {
    name  = "prometheus.prometheusSpec.remoteWrite[0].sigv4.enabled"
    value = "true"
  }

  depends_on = [aws_eks_cluster.this]
}