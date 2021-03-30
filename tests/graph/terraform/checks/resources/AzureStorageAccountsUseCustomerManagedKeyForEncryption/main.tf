data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "example" {
  name                = "examplekv"
  location            = "location"
  resource_group_name = "group"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  purge_protection_enabled = true
}

resource "azurerm_key_vault_key" "example" {
  name         = "tfex-key"
  key_vault_id = azurerm_key_vault.example.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt", "encrypt", "sign", "unwrapKey", "verify", "wrapKey"]
}


resource "azurerm_storage_account" "storage_account_good_1" {
  name                     = "examplestor"
  resource_group_name      = "group"
  location                 = "location"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "storage_account_bad_1" {
  name                     = "examplestor"
  resource_group_name      = "group"
  location                 = "location"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "storage_account_bad_2" {
  name                     = "examplestor"
  resource_group_name      = "group"
  location                 = "location"
  account_tier             = "Standard"
  account_replication_type = "GRS"

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account_customer_managed_key" "managed_key_good" {
  storage_account_id = azurerm_storage_account.storage_account_good_1.id
  key_vault_id       = azurerm_key_vault.example.id
  key_name           = azurerm_key_vault_key.example.name
  key_version = "1"
}


resource "azurerm_storage_account_customer_managed_key" "managed_key_bad_1" {
  storage_account_id = azurerm_storage_account.storage_account_bad_1.id
  key_vault_id       = ""
  key_name           = azurerm_key_vault_key.example.name
  key_version = "1"
}
