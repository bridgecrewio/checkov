resource "azurerm_servicebus_namespace" "pass" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  customer_managed_key {
    identity_id                       = "12345"
    key_vault_key_id                  = "yadaya"
    infrastructure_encryption_enabled = true
  }
  tags = {
    source = "terraform"
  }
}

resource "azurerm_servicebus_namespace" "fail" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  customer_managed_key {
    identity_id      = "12345"
    key_vault_key_id = "yadaya"
  }
  tags = {
    source = "terraform"
  }
}


resource "azurerm_servicebus_namespace" "fail2" {
  name                = "tfex-servicebus-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  customer_managed_key {
    identity_id                       = "12345"
    key_vault_key_id                  = "yadaya"
    infrastructure_encryption_enabled = false
  }
  tags = {
    source = "terraform"
  }
}