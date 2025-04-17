resource "aws_grafana_workspace" "this" {
  name                  = var.workspace_name
  account_access_type   = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type       = var.permission_type
  role_arn              = var.workspace_role_arn
  data_sources          = var.data_sources
  grafana_version       = "9.4"
}

resource "aws_grafana_workspace_api_key" "this" {
  key_name        = "terraform-integration"
  key_role        = "ADMIN"
  seconds_to_live = 2592000 # 30 days
  workspace_id    = aws_grafana_workspace.this.id
}

resource "aws_grafana_workspace_saml_configuration" "this" {
  workspace_id = aws_grafana_workspace.this.id
  role_values = {
    admin = ["admin"]
    editor = ["editor"]
    viewer = ["viewer"]
  }
  depends_on = [aws_grafana_workspace.this]
}

resource "aws_grafana_role_association" "admin" {
  role         = "ADMIN"
  user_ids     = var.admin_user_ids
  group_ids    = var.admin_group_ids
  workspace_id = aws_grafana_workspace.this.id
}

# Configure Prometheus data source
resource "aws_grafana_workspace_data_source" "prometheus" {
  count        = var.prometheus_workspace_id != "" ? 1 : 0
  workspace_id = aws_grafana_workspace.this.id
  name         = "prometheus"
  type         = "prometheus"
  
  # Custom configuration JSON for Prometheus data source
  configuration = jsonencode({
    access    = "proxy"
    isDefault = true
    jsonData = {
      httpMethod        = "GET"
      manageAlerts      = true
      prometheusType    = "AMP"
      sigV4Auth         = true
      sigV4AuthType     = "default"
      sigV4Region       = var.region
    }
    version = 1
  })
}