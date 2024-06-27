resource "azurerm_machine_learning_workspace" "pass1" {
  name                    = "example-workspace"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = "id3"
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_machine_learning_workspace" "pass2" {
  name                    = "example-workspace2"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = "id3"
  identity {
    type = "SystemAssigned"
  }

  public_network_access_enabled=false
}

resource "azurerm_machine_learning_workspace" "failed" {
  name                    = "example-workspace3"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = "id3"
  identity {
    type = "SystemAssigned"
  }

  public_network_access_enabled = true
}

