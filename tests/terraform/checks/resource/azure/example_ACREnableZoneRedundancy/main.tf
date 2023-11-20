
resource "azurerm_container_registry" "pass" {
  name                    = "containerRegistry1"
  resource_group_name     = azurerm_resource_group.example.name
  location                = azurerm_resource_group.example.location
  sku                     = "Premium"
  zone_redundancy_enabled = true
}


resource "azurerm_container_registry" "pass2" {
  name                    = "containerRegistry1"
  resource_group_name     = azurerm_resource_group.example.name
  location                = azurerm_resource_group.example.location
  sku                     = "Premium"
  zone_redundancy_enabled = true
  georeplications {
    location                = "East US"
    zone_redundancy_enabled = true
  }
  georeplications {
    location                = "North Europe"
    zone_redundancy_enabled = true
  }
}


resource "azurerm_container_registry" "fail" {
  name                = "containerRegistry1"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  sku                 = "Premium"
}


resource "azurerm_container_registry" "fail2" {
  name                    = "containerRegistry1"
  resource_group_name     = azurerm_resource_group.example.name
  location                = azurerm_resource_group.example.location
  sku                     = "Premium"
  zone_redundancy_enabled = false
}


resource "azurerm_container_registry" "fail3" {
  name                    = "containerRegistry1"
  resource_group_name     = azurerm_resource_group.example.name
  location                = azurerm_resource_group.example.location
  sku                     = "Premium"
  zone_redundancy_enabled = true
  georeplications {
    location = "East US"
  }
  georeplications {
    location                = "North Europe"
    zone_redundancy_enabled = true
  }
}
