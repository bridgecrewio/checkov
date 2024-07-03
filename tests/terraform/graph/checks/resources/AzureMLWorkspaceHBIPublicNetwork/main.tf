resource "azurerm_storage_account" "example" {
  name                     = "example-storage"
  resource_group_name      = "example-group"
  location                 = "West Europe"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  public_network_access_enabled = true
}

resource "azurerm_storage_account" "example-default" {
  name                     = "example-storage"
  resource_group_name      = "example-group"
  location                 = "West Europe"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "pass" {
  name                     = "example-storage"
  resource_group_name      = "example-group"
  location                 = "West Europe"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  public_network_access_enabled = false
}

resource "azurerm_machine_learning_workspace" "fail1" {
  name                    = "example-workspace2"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = azurerm_storage_account.example.id
  identity {
    type = "SystemAssigned"
  }

  high_business_impact = true

}
resource "azurerm_machine_learning_workspace" "fail2" {
  name                    = "example-workspace2"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = azurerm_storage_account.example-default.id
  identity {
    type = "SystemAssigned"
  }

  high_business_impact = true
}

resource "azurerm_machine_learning_workspace" "pass1" {
  name                    = "example-workspace2"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = azurerm_storage_account.example.id
  identity {
    type = "SystemAssigned"
  }

  high_business_impact = false

}

resource "azurerm_machine_learning_workspace" "pass2" {
  name                    = "example-workspace2"
  location                = "West Europe"
  resource_group_name     = "example-rg"
  application_insights_id = "id1"
  key_vault_id            = "id2"
  storage_account_id      = azurerm_storage_account.pass.id
  identity {
    type = "SystemAssigned"
  }

  high_business_impact = true
}