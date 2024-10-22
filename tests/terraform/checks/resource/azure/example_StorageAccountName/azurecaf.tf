provider "azurerm" {
  features {}
}

resource "azurecaf_name" "example" {
  random_length = 20
  resource_type = "azurerm_storage_account"
}

resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "azurecaf" {
  name                     = azurecaf_name.example.result
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}