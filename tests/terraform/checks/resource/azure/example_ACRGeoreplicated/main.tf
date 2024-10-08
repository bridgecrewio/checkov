resource "azurerm_container_registry" "fail" {
  name                          = var.acr.name
  resource_group_name           = var.acr.resource_group_name
  location                      = var.acr.location
  sku                           = "Basic"
  anonymous_pull_enabled        = var.anonymous_pull_enabled
  trust_policy_enabled          = var.trust_policy_enabled
  public_network_access_enabled = var.public_network_access


  dynamic "georeplications" {
    for_each = var.replications
    content {
      location                  = georeplications.value["location"]
      regional_endpoint_enabled = georeplications.value["regional_endpoint_enabled"]
      zone_redundancy_enabled   = georeplications.value["zone_redundancy_enabled"]
      tags                      = georeplications.value["tags"]
    }
  }
}

resource "azurerm_container_registry" "fail2" {
  name                          = var.acr.name
  resource_group_name           = var.acr.resource_group_name
  location                      = var.acr.location
  anonymous_pull_enabled        = var.anonymous_pull_enabled
  trust_policy_enabled          = var.trust_policy_enabled
  public_network_access_enabled = var.public_network_access


  dynamic "georeplications" {
    for_each = var.replications
    content {
      location                  = georeplications.value["location"]
      regional_endpoint_enabled = georeplications.value["regional_endpoint_enabled"]
      zone_redundancy_enabled   = georeplications.value["zone_redundancy_enabled"]
      tags                      = georeplications.value["tags"]
    }
  }
}

resource "azurerm_container_registry" "fail3" {
  name                          = var.acr.name
  resource_group_name           = var.acr.resource_group_name
  location                      = var.acr.location
  anonymous_pull_enabled        = var.anonymous_pull_enabled
  trust_policy_enabled          = var.trust_policy_enabled
  sku                           = "Premium"
  public_network_access_enabled = var.public_network_access
}

resource "azurerm_container_registry" "pass" {
  name                          = var.acr.name
  resource_group_name           = var.acr.resource_group_name
  location                      = var.acr.location
  anonymous_pull_enabled        = var.anonymous_pull_enabled
  trust_policy_enabled          = var.trust_policy_enabled
  sku                           = "Premium"
  public_network_access_enabled = var.public_network_access
  georeplications {
    location                  = var.georeplications.value["location"]
    regional_endpoint_enabled = var.georeplications.value["regional_endpoint_enabled"]
    zone_redundancy_enabled   = var.georeplications.value["zone_redundancy_enabled"]
    tags                      = var.georeplications.value["tags"]
  }
}
