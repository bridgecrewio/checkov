
resource "azurerm_storage_account" "fail" {
  name                            = "storageaccountname"
  resource_group_name             = azurerm_resource_group.example.name
  location                        = azurerm_resource_group.example.location
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  enable_https_traffic_only       = false
  allow_nested_items_to_be_public = true

  tags = {
    environment = "staging"
  }
}
resource "azurerm_storage_account" "pass" {
  name                            = "storageaccountname"
  resource_group_name             = azurerm_resource_group.example.name
  location                        = azurerm_resource_group.example.location
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  allow_nested_items_to_be_public = false
  tags = {
    environment = "staging"
  }
}

resource "azurerm_storage_account" "fail2" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"


  tags = {
    environment = "staging"
  }
}

