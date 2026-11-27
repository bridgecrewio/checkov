resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_postgresql_server" "pg_server_good_no_rule" {
  name                = "pg-good-no-rule"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  administrator_login          = "pud"
  administrator_login_password = "H@Sh1CoR3!" # checkov:skip=CKV_SECRET_6 test secret

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 5120
}

resource "azurerm_postgresql_server" "pg_server_good" {
  name                = "pg-good"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  administrator_login          = "pud"
  administrator_login_password = "H@Sh1CoR3!" # checkov:skip=CKV_SECRET_6 test secret

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 5120
}

resource "azurerm_postgresql_server" "pg_server_bad" {
  name                = "pg-bad"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  administrator_login          = "pud"
  administrator_login_password = "H@Sh1CoR3!" # checkov:skip=CKV_SECRET_6 test secret

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 5120
}

resource "azurerm_postgresql_firewall_rule" "firewall_rule_good" {
  name                = "FirewallRule1"
  resource_group_name = azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.pg_server_good.name
  start_ip_address    = "10.0.17.62"
  end_ip_address      = "10.0.17.62"
}

resource "azurerm_postgresql_firewall_rule" "firewall_rule_bad" {
  name                = "AllowAzureServices"
  resource_group_name = azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.pg_server_bad.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}
