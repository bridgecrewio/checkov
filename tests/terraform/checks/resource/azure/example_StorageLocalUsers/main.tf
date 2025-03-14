resource "azurerm_storage_account" "pass" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  local_user_enabled       = false
}

resource "azurerm_storage_account" "fail" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  local_user_enabled       = true
}

resource "azurerm_storage_account" "pass_missing_not_sftp" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

resource "azurerm_storage_account" "pass_missing_not_sftp2" {
  name                     = "examplename"
  resource_group_name      = "example"
  location                 = "eastus"
  account_tier             = "Standard"
  account_replication_type = "ZRS"
}

resource "azurerm_storage_account" "fail_missing_sftp" {
  name                     = "examplename"
  resource_group_name      = "example"
  location                 = "eastus"
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true
}

resource "azurerm_storage_account" "pass_sftp_local_user_disabled" {
  name                     = "examplename"
  resource_group_name      = "example"
  location                 = "eastus"
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true
  local_user_enabled       = false
}