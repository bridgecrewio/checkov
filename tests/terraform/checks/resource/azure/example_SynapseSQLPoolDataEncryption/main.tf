resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_synapse_workspace" "azurerm_synapse_workspace_example" {
  name                                 = "MyAzureSynapseWorkspace"
  resource_group_name                  = azurerm_resource_group.example.name
  location                             = azurerm_resource_group.example.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
  sql_administrator_login              = "sqladminuser"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_pass" {
  name                 = "examplesqlpool"
  data_encrypted       = true
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
  storage_account_type = "GRS"
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_fail_A" {
  name                 = "examplesqlpool"
  data_encrypted       = false
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
  storage_account_type = "GRS"
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_fail_B" {
  name                 = "examplesqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
  storage_account_type = "GRS"
}