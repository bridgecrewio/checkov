## SHOULD PASS: Premium tier SKU, explicitly disabled
resource "azurerm_container_registry" "ckv_unittest_pass_1" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  sku                    = "Premium"
  anonymous_pull_enabled = false
}

## SHOULD PASS: Premium tier SKU, disabled by default
resource "azurerm_container_registry" "ckv_unittest_pass_2" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Premium"
}

## SHOULD PASS: Standard tier SKU, disabled by default
resource "azurerm_container_registry" "ckv_unittest_pass_3" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
}

## SHOULD PASS: Basic tier should be ignored, anonymous_pull_enabled not supported
resource "azurerm_container_registry" "ckv_unittest_pass_4" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  sku                    = "Basic"
  anonymous_pull_enabled = true
}

## SHOULD PASS: No explicit tier defined scenario should be ignored, as of azurerm v2.96.0 sku defaults to Classic which is unsupported
resource "azurerm_container_registry" "ckv_unittest_pass_5" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  anonymous_pull_enabled = true
}

## SHOULD PASS: malformed SKU
resource "azurerm_container_registry" "ckv_unittest_pass_6" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  sku                    = []
  anonymous_pull_enabled = true
}

## SHOULD FAIL: Premium tier, explicitly enabled
resource "azurerm_container_registry" "ckv_unittest_fail_1" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  sku                    = "Premium"
  anonymous_pull_enabled = true
}

## SHOULD FAIL: Standard tier, explicitly enabled
resource "azurerm_container_registry" "ckv_unittest_fail_2" {
  name                   = "containerRegistry1"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  sku                    = "Standard"
  anonymous_pull_enabled = true
}
