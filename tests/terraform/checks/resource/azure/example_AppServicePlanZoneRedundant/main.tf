resource "azurerm_service_plan" "pass" {
  name                   = "example"
  resource_group_name    = azurerm_resource_group.example.name
  location               = azurerm_resource_group.example.location
  os_type                = "Linux"
  sku_name               = "P1v2"
  zone_balancing_enabled = true
}

resource "azurerm_service_plan" "fail1" {
  name                   = "example"
  resource_group_name    = azurerm_resource_group.example.name
  location               = azurerm_resource_group.example.location
  os_type                = "Linux"
  sku_name               = "P1v2"
  zone_balancing_enabled = false
}


resource "azurerm_service_plan" "fail2" {
  name                   = "example"
  resource_group_name    = azurerm_resource_group.example.name
  location               = azurerm_resource_group.example.location
  os_type                = "Linux"
  sku_name              = "P1v2"
}
