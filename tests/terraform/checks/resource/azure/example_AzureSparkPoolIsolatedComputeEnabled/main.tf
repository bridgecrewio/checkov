## SHOULD PASS: Explicit false
resource "synapse_spark_pool" "pass" {
  name                = "sparkPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  compute_isolation_enabled       = true
}

## SHOULD PASS: Default false
resource "synapse_spark_pool" "fail" {
  name                = "sparkPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

## SHOULD FAIL: Explicit true
resource "synapse_spark_pool" "fail2" {
  name                = "sparkPool1"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  compute_isolation_enabled       = false
}