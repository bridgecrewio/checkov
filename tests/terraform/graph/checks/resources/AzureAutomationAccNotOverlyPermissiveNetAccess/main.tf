# PASS case: public_network_access_enabled exists and public_network_access_enabled = "false".

resource "azurerm_automation_account" "pass" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku_name            = "Basic"
  public_network_access_enabled = "false"

  tags = {
    environment = "development"
  }
}

# FAIL case 1: public_network_access_enabled exists BUT public_network_access_enabled = "true".

resource "azurerm_automation_account" "fail_1" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku_name            = "Basic"
  public_network_access_enabled = true

  tags = {
    environment = "development"
  }
}

# FAIL case 2: public_network_access_enabled does NOT exist.

resource "azurerm_automation_account" "fail_2" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku_name            = "Basic"

  tags = {
    environment = "development"
  }
}