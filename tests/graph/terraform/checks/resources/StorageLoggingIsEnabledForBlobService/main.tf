resource "azurerm_resource_group" "blobExample_ok" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_log_analytics_workspace" "blobExample_ok" {
  name                = "exampleworkspace"
  location            = azurerm_resource_group.blobExample_ok.location
  resource_group_name = azurerm_resource_group.blobExample_ok.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_storage_account" "blobExample_ok" {
  name                     = "examplestoracc"
  resource_group_name      = azurerm_resource_group.blobExample_ok.name
  location                 = azurerm_resource_group.blobExample_ok.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_storage_insights" "blobExample_ok" {
  name                = "example-storageinsightconfig"
  resource_group_name = azurerm_resource_group.blobExample_ok.name
  workspace_id        = azurerm_log_analytics_workspace.blobExample_ok.id

  storage_account_id  = azurerm_storage_account.blobExample_ok.id
  storage_account_key = azurerm_storage_account.blobExample_ok.primary_access_key
  blob_container_names= ["blobExample_ok"]
}

resource "azurerm_storage_container" "blobExample_ok" {
  name                   = "my-awesome-content.zip"
  storage_account_name   = azurerm_storage_account.blobExample_ok.name
  storage_container_name = azurerm_storage_container.blobExample_ok.name
  container_access_type  = "blob"
}


resource "azurerm_storage_account" "blobExample_not_ok" {
  name                     = "examplestoracc"
  resource_group_name      = azurerm_resource_group.blobExample_not_ok.name
  location                 = azurerm_resource_group.blobExample_not_ok.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_storage_insights" "blobExample_not_ok" {
  name                = "example-storageinsightconfig"
  resource_group_name = azurerm_resource_group.blobExample_not_ok.name
  workspace_id        = azurerm_log_analytics_workspace.blobExample_not_ok.id

  storage_account_id  = azurerm_storage_account.blobExample_not_ok.id
  storage_account_key = azurerm_storage_account.blobExample_not_ok.primary_access_key
}

resource "azurerm_storage_container" "blobExample_not_ok" {
  name                   = "my-awesome-content.zip"
  storage_account_name   = azurerm_storage_account.blobExample_not_ok.name
  storage_container_name = azurerm_storage_container.blobExample_not_ok.name
  container_access_type  = "blob"
}


