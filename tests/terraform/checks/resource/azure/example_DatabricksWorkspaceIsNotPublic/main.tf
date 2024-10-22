resource "azurerm_databricks_workspace" "fail" {
  name                = "databricks-test"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "standard"

  tags = {
    Environment = "Production"
  }
}

resource "azurerm_databricks_workspace" "fail2" {
  name                          = "databricks-test"
  resource_group_name           = azurerm_resource_group.example.name
  location                      = azurerm_resource_group.example.location
  sku                           = "standard"
  public_network_access_enabled = true #Defaults to true

  tags = {
    Environment = "Production"
  }
}

resource "azurerm_databricks_workspace" "pass" {
  name                          = "databricks-test"
  resource_group_name           = azurerm_resource_group.example.name
  location                      = azurerm_resource_group.example.location
  sku                           = "standard"
  public_network_access_enabled = false

  tags = {
    Environment = "Production"
  }
}
