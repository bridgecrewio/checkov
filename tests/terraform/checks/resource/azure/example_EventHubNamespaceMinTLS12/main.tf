resource "azurerm_eventhub_namespace" "pass" {
  name                = "example-namespace"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  capacity            = 2
  minimum_tls_version = 1.2

  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventhub_namespace" "pass2" {
  name                = "eventhub-primary"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
}

resource "azurerm_eventhub_namespace" "fail" {
  name                = "eventhub-primary"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  sku                 = "Standard"
  minimum_tls_version = "1.1"
}