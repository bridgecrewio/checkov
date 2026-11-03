variable "admin_alerts" {
  type = bool
}

resource "azurerm_mssql_server_security_alert_policy" "example" {
  resource_group_name          = "example-resource-group"
  server_name                  = "example-sql-server"
  state                        = "Enabled"
  email_account_admins_enabled = var.admin_alerts
  retention_days               = 7
}
