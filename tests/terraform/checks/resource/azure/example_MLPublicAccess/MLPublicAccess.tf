## SHOULD PASS: Explicitly define parameter public_network_access_enabled to false
resource "azurerm_machine_learning_workspace" "ckv_unittest_pass" {
  name                          = "example-workspace"
  location                      = azurerm_resource_group.example.location
  resource_group_name           = azurerm_resource_group.example.name
  application_insights_id       = azurerm_application_insights.example.id
  key_vault_id                  = azurerm_key_vault.example.id
  storage_account_id            = azurerm_storage_account.example.id
  public_network_access_enabled = false

  identity {
    type = "SystemAssigned"
  }

  encryption {
    key_vault_id = azurerm_key_vault.example.id
    key_id       = azurerm_key_vault_key.example.id
  }
}


## SHOULD FAIL: Explicitly define parameter public_network_access_enabled to true
resource "azurerm_machine_learning_workspace" "ckv_unittest_fail" {
  name                          = "example-workspace"
  location                      = azurerm_resource_group.example.location
  resource_group_name           = azurerm_resource_group.example.name
  application_insights_id       = azurerm_application_insights.example.id
  key_vault_id                  = azurerm_key_vault.example.id
  storage_account_id            = azurerm_storage_account.example.id
  public_network_access_enabled = true

  identity {
    type = "SystemAssigned"
  }

  encryption {
    key_vault_id = azurerm_key_vault.example.id
    key_id       = azurerm_key_vault_key.example.id
  }
}

## SHOULD FAIL: Parameter public_network_access_enabled defaults to true
resource "azurerm_machine_learning_workspace" "ckv_unittest_fail_2" {
  name                    = "example-workspace"
  location                = azurerm_resource_group.example.location
  resource_group_name     = azurerm_resource_group.example.name
  application_insights_id = azurerm_application_insights.example.id
  key_vault_id            = azurerm_key_vault.example.id
  storage_account_id      = azurerm_storage_account.example.id

  identity {
    type = "SystemAssigned"
  }

  encryption {
    key_vault_id = azurerm_key_vault.example.id
    key_id       = azurerm_key_vault_key.example.id
  }
}
