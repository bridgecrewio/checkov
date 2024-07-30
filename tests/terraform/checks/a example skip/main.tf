
resource "azurerm_storage_account" "default" {
  #checkov:skip=CKV_AZURE_33
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "skip_more_than_one" {
  #checkov:skip=CKV_AZURE_33,CKV_AZURE_59: Skipped by user
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "skip_invalid" {
  #checkov:skip=CKV_AZURE_33,bla bla bla: Skipped by user
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
}