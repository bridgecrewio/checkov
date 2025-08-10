provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "pass" {
  name     = "pass-resources"
  location = "West Europe"
}

resource "azurerm_eventhub_namespace" "pass" {
  name                = "pass-eventhubns"
  location            = azurerm_resource_group.pass.location
  resource_group_name = azurerm_resource_group.pass.name
  sku                 = "Standard"
  capacity            = 2
  tags = {
    environment = "Production"
  }
}

resource "azurerm_resource_group" "pass2" {
  name     = "pass2-resources"
  location = "australiaeast"
}

resource "azurerm_eventhub_namespace" "pass2" {
  name                = "pass2-eventhubns"
  location            = azurerm_resource_group.pass2.location
  resource_group_name = azurerm_resource_group.pass2.name
  sku                 = "Standard"
  capacity            = 2
  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventhub_namespace" "unknown" {
  name                = "unknown-eventhubns"
  location            = azurerm_resource_group.foo.location
  resource_group_name = azurerm_resource_group.foo.name
  sku                 = "Standard"
  capacity            = 2
  tags = {
    environment = "Production"
  }
}

resource "azurerm_resource_group" "fail" {
  name     = "fail-resources"
  location = "South Africa West"
}

resource "azurerm_eventhub_namespace" "fail" {
  name                = "fail-eventhubns"
  location            = azurerm_resource_group.fail.location
  resource_group_name = azurerm_resource_group.fail.name
  sku                 = "Standard"
  capacity            = 2
  tags = {
    environment = "Production"
  }
}