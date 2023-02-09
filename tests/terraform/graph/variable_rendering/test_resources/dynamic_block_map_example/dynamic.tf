data "azurerm_resource_group" "abc-azr-lab" {
  name = "abc-azr-lab"
}

resource "azurerm_network_security_group" "dynamic_nsg_fail" {
  name                = var.nsg_name_fail
  location            = data.azurerm_resource_group.abc-azr-lab.location
  resource_group_name = data.azurerm_resource_group.abc-azr-lab.name

  dynamic "security_rule" {
    for_each = var.fail_nsg_rules
    content {
      name                       = security_rule.value["name"]
      priority                   = security_rule.value["priority"]
      direction                  = security_rule.value["direction"]
      access                     = security_rule.value["access"]
      protocol                   = security_rule.value["protocol"]
      source_port_range          = security_rule.value["source_port_range"]
      destination_port_range     = security_rule.value["destination_port_range"]
      source_address_prefix      = security_rule.value["source_address_prefix"]
      destination_address_prefix = security_rule.value["destination_address_prefix"]
    }
  }
}

resource "azurerm_network_security_group" "dynamic_nsg_pass" {
  name                = var.nsg_name_pass
  location            = data.azurerm_resource_group.abc-azr-lab.location
  resource_group_name = data.azurerm_resource_group.abc-azr-lab.name

  dynamic "security_rule" {
    for_each = var.pass_nsg_rules
    content {
      name                       = security_rule.value["name"]
      priority                   = security_rule.value["priority"]
      direction                  = security_rule.value["direction"]
      access                     = security_rule.value["access"]
      protocol                   = security_rule.value["protocol"]
      source_port_range          = security_rule.value["source_port_range"]
      destination_port_range     = security_rule.value["destination_port_range"]
      source_address_prefix      = security_rule.value["source_address_prefix"]
      destination_address_prefix = security_rule.value["destination_address_prefix"]
    }
  }
}