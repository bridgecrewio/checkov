# not azurerm_storage_sync resource
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

# fail
resource "azurerm_storage_sync" "fail1" {
  name                = "example-storage-sync1"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  tags = {
    foo = "bar"
  }
  incoming_traffic_policy = "AllowAllTraffic"
}

# pass
resource "azurerm_storage_sync" "pass" {
  name                = "example-storage-sync2"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  tags = {
    foo = "bar"
  }
  incoming_traffic_policy = "AllowVirtualNetworksOnly"
}

# fail - Default set to AllowAllTraffic
resource "azurerm_storage_sync" "fail2" {
  name                = "example-storage-sync3"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  tags = {
    foo = "bar"
  }
}