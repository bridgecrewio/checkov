## SHOULD PASS: Explicitly set to false
resource "azurerm_container_registry" "ckv_unittest_pass" {
  name                          = "containerRegistry1"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  public_network_access_enabled = false
}


## SHOULD FAIL: Explicitly set to true
resource "azurerm_container_registry" "ckv_unittest_fail" {
  name                          = "containerRegistry1"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  public_network_access_enabled = true
}

## SHOULD FAIL: Not set, default is true
resource "azurerm_container_registry" "ckv_unittest_fail_2" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}