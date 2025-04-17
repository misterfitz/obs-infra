resource "aws_prometheus_workspace" "this" {
  alias             = var.workspace_alias
  # retention_in_days = var.retention_in_days
}

resource "aws_prometheus_alert_manager_definition" "this" {
  workspace_id = aws_prometheus_workspace.this.id
  definition   = <<EOF
alertmanager_config: |
  global:
    resolve_timeout: 5m
  route:
    receiver: 'default'
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 12h
    group_by: ['alertname', 'severity']
  receivers:
    - name: 'default'
EOF
}

resource "aws_prometheus_rule_group_namespace" "this" {
  name         = "default-rules"
  workspace_id = aws_prometheus_workspace.this.id
  data         = <<EOF
groups:
  - name: node-exporter
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage detected
          description: "CPU usage is above 80% for 5 minutes (current value: {{ $value }}%)"
  - name: memory-alerts
    rules:
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage detected
          description: "Memory usage is above 80% for 5 minutes (current value: {{ $value }}%)"
  - name: disk-alerts
    rules:
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High disk usage detected
          description: "Disk usage is above 85% for 5 minutes (current value: {{ $value }}%)"
EOF
}