# PASS case: resources are connected and network_rules block contains all the required arguments

resource "azurerm_storage_account" "pass" {
  name                = "pass"
  resource_group_name = azurerm_resource_group.pud_rg.name

  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "staging"
  }

}

resource "azurerm_private_endpoint" "dep-pep-j1-10-rlp-76252" {
  name                = "dep-pep-j1-10-rlp-76252"
  resource_group_name = azurerm_resource_group.pud_rg.name
  location            = azurerm_resource_group.pud_rg.location
  subnet_id           = azurerm_subnet.pud-subn.id
  private_service_connection {
    name                           = "policyauto3"
    private_connection_resource_id = azurerm_storage_account.pass.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }
}

# FAIL case: azurerm_private_endpoint resource is not connected

resource "azurerm_storage_account" "fail" {
  name                     = "fail"
  resource_group_name      = azurerm_resource_group.pud_rg.name
  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}
