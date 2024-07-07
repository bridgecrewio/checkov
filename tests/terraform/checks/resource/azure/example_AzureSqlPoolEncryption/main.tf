## SHOULD PASS: Explicit true
resource "synapse_sql_pool" "pass" {
  name                = "sqlPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  data_encrypted       = true
}

## SHOULD FAIL: Default false
resource "synapse_sql_pool" "fail1" {
  name                = "sqlPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

## SHOULD FAIL: Explicit false
resource "synapse_sql_pool" "fail2" {
  name                = "sqlPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  data_encrypted       = false
}