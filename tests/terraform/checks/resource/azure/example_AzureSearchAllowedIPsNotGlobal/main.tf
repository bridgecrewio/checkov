# pass

resource "azurerm_search_service" "default" {
  name                = "example-search-service"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "standard"
}

resource "azurerm_search_service" "private" {
  name                = "example-search-service"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "standard"
  allowed_ips         = ["10.0.0.0/16"]
}

# fail

resource "azurerm_search_service" "public" {
  name                          = "example-search-service"
  resource_group_name           = azurerm_resource_group.example.name
  location                      = azurerm_resource_group.example.location
  sku                           = "standard"
  allowed_ips         = ["0.0.0.0/0"]
}
