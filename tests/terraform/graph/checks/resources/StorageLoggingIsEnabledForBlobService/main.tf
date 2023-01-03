resource "azurerm_resource_group" "resource_group_ok" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_log_analytics_workspace" "analytics_workspace_ok" {
  name                = "exampleworkspace"
  location            = azurerm_resource_group.resource_group_ok.location
  resource_group_name = azurerm_resource_group.resource_group_ok.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# pass

resource "azurerm_storage_account" "storage_account_ok" {
  name                     = "examplestoracc"
  resource_group_name      = azurerm_resource_group.resource_group_ok.name
  location                 = azurerm_resource_group.resource_group_ok.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_storage_insights" "analytics_storage_insights_ok" {
  name                = "example-storageinsightconfig"
  resource_group_name = azurerm_resource_group.resource_group_ok.name
  workspace_id        = azurerm_log_analytics_workspace.analytics_workspace_ok.id

  storage_account_id  = azurerm_storage_account.storage_account_ok.id
  storage_account_key = azurerm_storage_account.storage_account_ok.primary_access_key
  blob_container_names= ["blobExample_ok"]
}

resource "azurerm_storage_container" "storage_container_ok" {
  name                   = "my-awesome-content.zip"
  storage_account_name   = azurerm_storage_account.storage_account_ok.name
  storage_container_name = azurerm_storage_container.storage_container_ok.name
  container_access_type  = "blob"
}

resource "azurerm_storage_account" "storage_account_ok_private" {
  name                     = "examplestoracc"
  resource_group_name      = azurerm_resource_group.resource_group_ok.name
  location                 = azurerm_resource_group.resource_group_ok.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_storage_insights" "storage_account_ok_private" {
  name                = "example-storageinsightconfig"
  resource_group_name = azurerm_resource_group.resource_group_ok.name
  workspace_id        = azurerm_log_analytics_workspace.analytics_workspace_ok.id

  storage_account_id  = azurerm_storage_account.storage_account_ok_private.id
  storage_account_key = azurerm_storage_account.storage_account_ok_private.primary_access_key
  blob_container_names= ["blobExample_ok"]
}

resource "azurerm_storage_container" "storage_account_ok_private" {
  name                   = "my-awesome-content.zip"
  storage_account_name   = azurerm_storage_account.storage_account_ok_private.name
  storage_container_name = azurerm_storage_container.storage_account_ok_private.name
  container_access_type  = "private"
}

# fail

resource "azurerm_storage_account" "storage_account_not_ok" {
  name                     = "examplestoracc"
  resource_group_name      = azurerm_resource_group.blobExample_not_ok.name
  location                 = azurerm_resource_group.blobExample_not_ok.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_storage_insights" "storage_insights_not_ok" {
  name                = "example-storageinsightconfig"
  resource_group_name = azurerm_resource_group.blobExample_not_ok.name
  workspace_id        = azurerm_log_analytics_workspace.blobExample_not_ok.id

  storage_account_id  = azurerm_storage_account.storage_account_not_ok.id
  storage_account_key = azurerm_storage_account.storage_account_not_ok.primary_access_key
}

resource "azurerm_storage_container" "storage_container_not_ok" {
  name                   = "my-awesome-content.zip"
  storage_account_name   = azurerm_storage_account.storage_account_not_ok.name
  storage_container_name = azurerm_storage_container.storage_container_not_ok.name
  container_access_type  = "blob"
}


