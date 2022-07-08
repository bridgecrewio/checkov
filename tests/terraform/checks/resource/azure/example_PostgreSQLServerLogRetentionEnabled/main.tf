resource "azurerm_postgresql_configuration" "fail" {
  name                = "log_retention"
  resource_group_name = data.azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.example.name
  value               = "off"
}

resource "azurerm_postgresql_configuration" "pass" {
  name                = "log_retention"
  resource_group_name = data.azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.example.name
  value               = "on"
}
