resource "azurerm_mssql_database_extended_auditing_policy" "fail" {
  database_id                             = azurerm_mssql_database.examplea.id
  storage_endpoint                        = azurerm_storage_account.examplea.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.examplea.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 89
  log_monitoring_enabled                  = false
}

resource "azurerm_mssql_database_extended_auditing_policy" "fail2" {
  database_id                             = azurerm_mssql_database.examplea.id
  storage_endpoint                        = azurerm_storage_account.examplea.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.examplea.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 89
}

resource "azurerm_mssql_database_extended_auditing_policy" "pass" {
  database_id                             = azurerm_mssql_database.examplea.id
  storage_endpoint                        = azurerm_storage_account.examplea.primary_blob_endpoint
  storage_account_access_key              = azurerm_storage_account.examplea.primary_access_key
  storage_account_access_key_is_secondary = false
  retention_in_days                       = 89
  log_monitoring_enabled                  = true
}