
resource "azurerm_storage_account" "fail" {
  name                          = "storageaccountname"
  resource_group_name           = azurerm_resource_group.example.name
  location                      = azurerm_resource_group.example.location
  account_tier                  = "Standard"
  account_replication_type      = "GRS"
  enable_https_traffic_only     = false
  public_network_access_enabled = true

  tags = {
    environment = "staging"
  }
}
resource "azurerm_storage_account" "pass" {
  name                          = "storageaccountname"
  resource_group_name           = azurerm_resource_group.example.name
  location                      = azurerm_resource_group.example.location
  account_tier                  = "Standard"
  account_replication_type      = "GRS"
  public_network_access_enabled = false
  tags = {
    environment = "staging"
  }
}

resource "azurerm_storage_account" "fail2" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"


  tags = {
    environment = "staging"
  }
}

resource "azurerm_storage_account" "pass_network_access_disabled" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  public_network_access    = "Disabled"
}

resource "azurerm_storage_account" "pass_network_access_perimeter" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  public_network_access    = "SecuredByPerimeter"
}

resource "azurerm_storage_account" "fail_network_access_enabled" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  public_network_access    = "Enabled"
}

