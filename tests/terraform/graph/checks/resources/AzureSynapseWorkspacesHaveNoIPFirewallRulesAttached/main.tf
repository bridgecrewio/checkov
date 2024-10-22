resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_synapse_workspace" "workspace_good" {
  name                                 = "example"
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
  managed_virtual_network_enabled      = true
  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_workspace" "workspace_bad" {
  name                                 = "example"
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_firewall_rule" "firewall_rule" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.workspace_bad.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}