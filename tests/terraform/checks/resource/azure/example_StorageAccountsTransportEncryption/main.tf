# pass

resource "azurerm_storage_account" "default" {
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "enabled" {
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only = true
}

# fail

resource "azurerm_storage_account" "disabled" {
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  enable_https_traffic_only = false
}
