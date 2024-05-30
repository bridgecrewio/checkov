resource "azurerm_databricks_workspace" "databricks_workspace_bad" {
  name                        = "example"
  location                    = "location"
  resource_group_name         = "group"
  sku                         = "premium"
  managed_resource_group_name = "example"
}


resource "azurerm_databricks_workspace" "databricks_workspace_good" {
  name                        = "example"
  location                    = "location"
  resource_group_name         = "group"
  sku                         = "premium"
  managed_resource_group_name = "example"
  customer_managed_key_enabled = true
}

resource "azurerm_databricks_workspace_root_dbfs_customer_managed_key" "databricks_workspace_good" {
  workspace_id     = azurerm_databricks_workspace.databricks_workspace_good.id
  key_vault_key_id = "123456"
}