## SHOULD PASS: Explicit false
resource "azurerm_container_registry" "ckv_unittest_pass" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  admin_enabled       = false
}

## SHOULD PASS: Default false
resource "azurerm_container_registry" "ckv_unittest_pass_2" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

## SHOULD FAIL: Explicit true
resource "azurerm_container_registry" "ckv_unittest_fail" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  admin_enabled       = true
}