
resource "azurerm_container_registry" "pass" {
  name                      = "containerRegistry1"
  resource_group_name       = azurerm_resource_group.rg.name
  location                  = azurerm_resource_group.rg.location
  sku                       = "Premium"
  anonymous_pull_enabled    = false
  quarantine_policy_enabled = true
  retention_policy_in_days  = 7
}


resource "azurerm_container_registry" "fail" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Premium"
}
