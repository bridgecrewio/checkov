resource "azurerm_app_service_environment_v3" "pass" {
  name                = "example-asev3"
  resource_group_name = azurerm_resource_group.example.name
  subnet_id           = azurerm_subnet.example.id
  zone_redundant      = true

  tags = {
    env         = "production"
    terraformed = "true"
  }
}

resource "azurerm_app_service_environment_v3" "fail1" {
  name                = "example-asev3"
  resource_group_name = azurerm_resource_group.example.name
  subnet_id            = azurerm_subnet.example.id
  zone_redundant       = false

  tags = {
    env         = "production"
    terraformed = "true"
  }
}

resource "azurerm_app_service_environment_v3" "fail2" {
  name                = "example-asev3"
  resource_group_name = azurerm_resource_group.example.name
  subnet_id            = azurerm_subnet.example.id

  tags = {
    env         = "production"
    terraformed = "true"
  }
}