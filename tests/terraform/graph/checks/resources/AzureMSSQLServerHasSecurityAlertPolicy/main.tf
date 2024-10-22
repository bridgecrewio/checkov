resource "azurerm_sql_server" "sql_server_good_1" {
  name                         = "mysqlserver"
  resource_group_name          = "group"
  location                     = "location"
  version                      = "12.0"
  administrator_login          = "4dm1n157r470r"
  administrator_login_password = "4-v3ry-53cr37-p455w0rd"  # checkov:skip=CKV_SECRET_6 test secret
}

resource "azurerm_sql_server" "sql_server_good_2" {
  name                         = "mysqlserver"
  resource_group_name          = "group"
  location                     = "location"
  version                      = "12.0"
  administrator_login          = "4dm1n157r470r"
  administrator_login_password = "4-v3ry-53cr37-p455w0rd"
}

resource "azurerm_sql_server" "sql_server_bad_1" {
  name                         = "mysqlserver"
  resource_group_name          = "group"
  location                     = "location"
  version                      = "12.0"
  administrator_login          = "4dm1n157r470r"
  administrator_login_password = "4-v3ry-53cr37-p455w0rd"
}

resource "azurerm_mssql_server_security_alert_policy" "alert_policy_good" {
  resource_group_name        = "group"
  server_name                = azurerm_sql_server.sql_server_good_1.name
  state                      = "Enabled"
  retention_days = 20
}

resource "azurerm_mssql_server_security_alert_policy" "alert_policy_bad" {
  resource_group_name        = "group"
  server_name                = azurerm_sql_server.sql_server_bad_1.name
  state                      = "Disabled"
  retention_days = 20
}