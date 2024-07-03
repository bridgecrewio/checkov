resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_synapse_workspace" "azurerm_synapse_workspace_example" {
  name                                 = "example"
  resource_group_name                  = azurerm_resource_group.example.name
  location                             = azurerm_resource_group.example.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "H@Sh1CoR3!"

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "00000000-0000-0000-0000-000000000000"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Env = "production"
  }
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_pass_A" {
  name                 = "examplesqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_pass_B" {
  name                 = "examplesqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_fail_A" {
  name                 = "examplesqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
}

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_fail_B" {
  name                 = "examplesqlpool"
  synapse_workspace_id = azurerm_synapse_workspace.azurerm_synapse_workspace_example.id
  sku_name             = "DW100c"
  create_mode          = "Default"
}


resource "azurerm_synapse_sql_pool_extended_auditing_policy" "extended_auditing_policy_enabled" {
  sql_pool_id                             = azurerm_synapse_sql_pool.azurerm_synapse_sql_pool_pass_A.id
  log_monitoring_enabled                  = true
  storage_endpoint                        = azurerm_storage_account.audit_logs.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.audit_logs.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 6
}

resource "azurerm_synapse_sql_pool_extended_auditing_policy" "extended_auditing_policy_enabled_by_default" {
  sql_pool_id                             = azurerm_synapse_sql_pool.azurerm_synapse_sql_pool_pass_B.id
  storage_endpoint                        = azurerm_storage_account.audit_logs.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.audit_logs.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 6
}

resource "azurerm_synapse_sql_pool_extended_auditing_policy" "extended_auditing_policy_disabled" {
  sql_pool_id                             = azurerm_synapse_sql_pool.azurerm_synapse_sql_pool_fail_B.id
  log_monitoring_enabled                  = false
  storage_endpoint                        = azurerm_storage_account.audit_logs.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.audit_logs.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 6
}
