resource "azurerm_eventgrid_topic" "fail" {
  name                = "my-eventgrid-topic"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventgrid_topic" "fail2" {
  name                = "my-eventgrid-topic"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
local_auth_enabled = true
  tags = {
    environment = "Production"
  }
}

resource "azurerm_eventgrid_topic" "pass" {
  name                = "my-eventgrid-topic"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
local_auth_enabled = false
  tags = {
    environment = "Production"
  }
}