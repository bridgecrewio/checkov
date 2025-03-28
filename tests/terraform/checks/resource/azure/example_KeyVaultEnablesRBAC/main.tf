resource "azurerm_key_vault" "pass" {
  name                                   = "pass"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  public_network_access_enabled          = false
  sku_name                               = "standard"
  enable_rbac_authorization              = true
  
}

resource "azurerm_key_vault" "fail" {
  name                                   = "fail"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  public_network_access_enabled          = false
  sku_name                               = "standard"
  enable_rbac_authorization              = false
  
}

resource "azurerm_key_vault" "fail1" {
  name                                   = "fail1"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  public_network_access_enabled          = false
  sku_name                               = "standard"

}