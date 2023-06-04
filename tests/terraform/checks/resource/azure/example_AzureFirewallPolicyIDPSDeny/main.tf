resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_firewall_policy" "fail" {
  name                = "fail"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
}


resource "azurerm_firewall_policy" "fail2" {
  name                = "fail2"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  intrusion_detection {
    mode = "Off"
  }
}

resource "azurerm_firewall_policy" "pass" {
  name                = "pass"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  intrusion_detection {
    mode = "Deny"
  }
}