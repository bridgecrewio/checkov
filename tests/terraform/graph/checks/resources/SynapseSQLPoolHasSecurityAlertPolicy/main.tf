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

resource "azurerm_synapse_sql_pool" "azurerm_synapse_sql_pool_pass" {
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

resource "azurerm_storage_account" "audit_logs" {
  name                     = "examplesa"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_synapse_sql_pool_security_alert_policy" "azurerm_synapse_sql_pool_security_alert_policy_enabled" {
  sql_pool_id                = azurerm_synapse_sql_pool.azurerm_synapse_sql_pool_pass.id
  policy_state               = "Enabled"
  storage_endpoint           = azurerm_storage_account.audit_logs.primary_blob_endpoint
  storage_account_access_key = azurerm_storage_account.audit_logs.primary_access_key
  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}

resource "azurerm_synapse_sql_pool_security_alert_policy" "azurerm_synapse_sql_pool_security_alert_policy_disabled" {
  sql_pool_id                = azurerm_synapse_sql_pool.azurerm_synapse_sql_pool_fail_B.id
  policy_state               = "Disabled"
  storage_endpoint           = azurerm_storage_account.audit_logs.primary_blob_endpoint
  storage_account_access_key = azurerm_storage_account.audit_logs.primary_access_key
  disabled_alerts = [
    "Sql_Injection",
    "Data_Exfiltration"
  ]
  retention_days = 20
}