# PASS Case: "service_uri" starts with https://

resource "azurerm_container_registry_webhook" "pass" {
  name                = "pudwebhook"
  resource_group_name = azurerm_resource_group.pudrg.name
  registry_name       = azurerm_container_registry.acr.name
  location            = azurerm_resource_group.pudrg.location

  service_uri = "https://pudwebhookreceiver.pud/prx"
  status      = "enabled"
  scope       = "prx:*"
  actions     = ["push"]
  custom_headers = {
    "Content-Type" = "application/json"
  }
}

# FAIL Case: "service_uri" does NOT start with https:// 

resource "azurerm_container_registry_webhook" "fail" {
  name                = "pudwebhook"
  resource_group_name = azurerm_resource_group.pudrg.name
  registry_name       = azurerm_container_registry.acr.name
  location            = azurerm_resource_group.pudrg.location

  service_uri = "http://pudwebhookreceiver.pud/prx"
  status      = "enabled"
  scope       = "prx:*"
  actions     = ["push"]
  custom_headers = {
    "Content-Type" = "application/json"
  }
}