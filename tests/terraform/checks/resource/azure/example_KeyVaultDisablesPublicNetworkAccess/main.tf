resource "azurerm_key_vault" "pass1" {
  name                                   = "examplepass1"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  public_network_access_enabled          = false
  sku_name                               = "standard"
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
}

resource "azurerm_key_vault" "pass2" {
  name                                   = "examplepass2"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  public_network_access_enabled          = false
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
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
}

resource "azurerm_key_vault" "pass3" {
  name                                   = "examplepass3"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  public_network_access_enabled          = true
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
    ip_rules = ["127.0.0.1"]
  }
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
}

resource "azurerm_key_vault" "pass4" {
  name                                   = "examplepass4"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
    ip_rules = ["127.0.0.1"]
  }
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
}

resource "azurerm_key_vault" "pass5" {
  name                                   = "examplepass5"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
    virtual_network_subnet_ids = ["127.0.0.1/24"]
  }
}

resource "azurerm_key_vault" "fail1" {
  name                                   = "examplefail1"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
  public_network_access_enabled          = true
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
}

resource "azurerm_key_vault" "fail2" {
  name                                   = "examplefail2"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
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
}

resource "azurerm_key_vault" "fail3" {
  name                                   = "examplefail3"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
    ip_rules = []
  }
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
}

resource "azurerm_key_vault" "fail4" {
  name                                   = "examplefail4"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"
  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }
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
}



resource "azurerm_key_vault" "fail5" {
  name                                   = "examplefail5"
  location                               = azurerm_resource_group.example.location
  resource_group_name                    = azurerm_resource_group.example.name
  enabled_for_disk_encryption            = true
  tenant_id                              = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days             = 90
  purge_protection_enabled               = enabled
  sku_name                               = "standard"

  dynamic "network_acls" {
    for_each = var.nacls_enabled ? [1] : []
    content {
      default_action             = "Allow"
      bypass                     = "AzureServices"
      ip_rules                   = []
      virtual_network_subnet_ids = []
    }
  }
}
