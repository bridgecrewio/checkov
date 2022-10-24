data "azurerm_client_config" "current" {}
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West US"
}


#fail
resource "azurerm_cognitive_account" "cognitive_account_bad" {
  name                = "example-account"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  kind                = "Face"
  sku_name            = "S0"
}


#pass
resource "azurerm_cognitive_account" "cognitive_account_good" {
  name                  = "example-account"
  location              = azurerm_resource_group.example.location
  resource_group_name   = azurerm_resource_group.example.name
  kind                  = "Face"
  sku_name              = "E0"
  public_network_access_enabled = false
}

resource "azurerm_key_vault" "good_vault" {
  name                     = "example-vault"
  location                 = azurerm_resource_group.example.location
  resource_group_name      = azurerm_resource_group.example.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
}

resource "azurerm_key_vault_key" "good_key" {
  name         = "example-key"
  key_vault_id = azurerm_key_vault.good_vault.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt", "encrypt", "sign", "unwrapKey", "verify", "wrapKey"]
}

resource "azurerm_cognitive_account_customer_managed_key" "good_cmk" {
  cognitive_account_id = azurerm_cognitive_account.cognitive_account_good.id
  key_vault_key_id     = azurerm_key_vault_key.good_key.id
}