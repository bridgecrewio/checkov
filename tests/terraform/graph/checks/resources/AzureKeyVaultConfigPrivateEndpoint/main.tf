# PASS case: Keyvault is connected to private endpoint

resource "azurerm_key_vault" "pass" {
  name                        = "pass"
  location                    = azurerm_resource_group.dep-rg-j1-1-rlp-72704.location
  resource_group_name         = azurerm_resource_group.dep-rg-j1-1-rlp-72704.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
    ]

    secret_permissions = [
      "Get",
    ]

    storage_permissions = [
      "Get",
    ]
  }
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"

  }
}

resource "azurerm_private_endpoint" "pud_privendpt" {
  name                = "pud_privendpt"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  subnet_id           = azurerm_subnet.dep_pud_subn.id

  private_service_connection {
    name                           = "kv-privateserviceconnection"
    private_connection_resource_id = azurerm_key_vault.pass.id
    is_manual_connection           = false
    subresource_names = ["vault"]
  }
}


# FAIL case key vault is NOT connected to private endpoint

resource "azurerm_key_vault" "fail" {
  name                        = "fail"
  location                    = azurerm_resource_group.dep-rg-j1-1-rlp-72704.location
  resource_group_name         = azurerm_resource_group.dep-rg-j1-1-rlp-72704.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
    ]

    secret_permissions = [
      "Get",
    ]

    storage_permissions = [
      "Get",
    ]
  }
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"

  }
}


locals {
  should_use = false
}


resource "azurerm_private_endpoint" "private_endpoint_pod_empty_count" {
  count = local.should_use == true ? 1 : 0
  name = "${azurerm_key_vault.empty_count.name}-test"
  location = azurerm_resource_group.cfg.location
  resource_group_name = azurerm_resource_group.cfg.name
  subnet_id = data.azurerm_subnet.private_end_point_subnet[0].id
  tags = var.tags
  private_service_connection {
    is_manual_connection = false
    name = "${azurerm_key_vault.empty_count.name}-test"
    private_connection_resource_id = azurerm_key_vault.empty_count.id
    subresource_names = ["vault"]
  }
}

resource "azurerm_key_vault" "empty_count" {
  location            = ""
  name                = "test"
  resource_group_name = ""
  sku_name            = ""
  tenant_id           = ""
}