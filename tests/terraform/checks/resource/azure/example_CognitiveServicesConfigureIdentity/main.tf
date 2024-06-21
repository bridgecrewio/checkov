resource "azurerm_cognitive_account" "pass" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "Face"
  identity {
    type = "a"
  }
  sku_name = "S0"

  tags = {
    Acceptance = "Test"
  }
}

resource "azurerm_cognitive_account" "fail" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "Face"
  local_auth_enabled = true

  sku_name = "S0"

  tags = {
    Acceptance = "Test"
  }
}