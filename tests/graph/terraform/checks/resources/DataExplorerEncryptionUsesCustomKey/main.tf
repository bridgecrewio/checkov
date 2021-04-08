resource "azurerm_kusto_cluster" "cluster_ok" {
  name                = "kustocluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku {
    name     = "Standard_D13_v2"
    capacity = 2
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_kusto_cluster_customer_managed_key" "example" {
  cluster_id   = azurerm_kusto_cluster.cluster_ok.id
  key_vault_id = azurerm_key_vault.example.id
  key_name     = azurerm_key_vault_key.example.name
  key_version  = azurerm_key_vault_key.example.version
}


resource "azurerm_kusto_cluster" "cluster_ok_not_ok" {
  name                = "kustocluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku {
    name     = "Standard_D13_v2"
    capacity = 2
  }

  identity {
    type = "SystemAssigned"
  }
}