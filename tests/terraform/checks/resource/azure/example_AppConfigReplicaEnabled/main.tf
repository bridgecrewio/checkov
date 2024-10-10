resource "azurerm_app_configuration" "fail" {
  name                       = "appConf2"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  sku                        = "standard"
  local_auth_enabled         = true
  public_network_access      = "Enabled"
  purge_protection_enabled   = true
  soft_delete_retention_days = 1

}

resource "azurerm_app_configuration" "pass" {
  name                       = "appConf2"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  sku                        = "standard"
  local_auth_enabled         = true
  public_network_access      = "Enabled"
  purge_protection_enabled   = false
  soft_delete_retention_days = 1

  replica {
    name     = "replica1"
    location = "West US"
  }

}