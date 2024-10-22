resource "azurerm_servicebus_namespace" "pass" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  minimum_tls_version="1.2"
  customer_managed_key {
    identity_id                       = "12345"
    key_vault_key_id                  = "yadaya"
    infrastructure_encryption_enabled = true
  }
  identity {
    type = "SystemAssigned"
  }
  local_auth_enabled = false
  tags = {
    source = "terraform"
  }
}

resource "azurerm_servicebus_namespace" "fail" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"

  tags = {
    source = "terraform"
  }
}

resource "azurerm_servicebus_namespace" "fail2" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  local_auth_enabled = true
  minimum_tls_version="1.0"
  tags = {
    source = "terraform"
  }
}
