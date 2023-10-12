resource "azurerm_automation_account" "pass" {
  name                = "pud-automatix"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"
  identity {
    type = "SystemAssigned, UserAssigned"
  }

}

resource "azurerm_automation_account" "fail_1" {
  name                = "pud-automatix"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"

}


resource "azurerm_automation_account" "fail_2" {
  name                = "pud-automatix"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"
  identity {
    type = " "
  }

}