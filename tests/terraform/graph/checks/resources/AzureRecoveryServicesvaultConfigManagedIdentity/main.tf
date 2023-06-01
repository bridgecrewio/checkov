resource "azurerm_recovery_services_vault" "pass" {
  name                = "pud-recovery-vault"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"
  identity {
    type = "SystemAssigned, UserAssigned"
  }

}

resource "azurerm_recovery_services_vault" "fail_1" {
  name                = "pud-recovery-vault"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"

}


resource "azurerm_recovery_services_vault" "fail_2" {
  name                = "pud-recovery-vault"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  sku                 = "Standard"
  identity {
    type = " "
  }

}