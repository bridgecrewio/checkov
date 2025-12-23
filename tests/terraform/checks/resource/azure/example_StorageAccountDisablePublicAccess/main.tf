
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

resource "azurerm_storage_account" "pass2" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  network_rules {
    default_action = "Deny"
    virtual_network_subnet_ids = [
      "/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/example-rg/providers/Microsoft.Network/virtualNetworks/example-vnet/subnets/example-subnet"
    ]
  }

  tags = {
    environment = "staging"
  }
}