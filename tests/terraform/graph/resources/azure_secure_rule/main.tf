resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_network_security_group" "example" {
  name                = "acceptanceTestSecurityGroup1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}

resource "azurerm_network_security_group" "sg_fail" {
  # this will fail DoNotUseInlineRule
  name                = "sg-fail"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule = [
    {
      name                    = "rule_we_care_about"
      source_address_prefixes = ["allowed_ip"]
    },
    {
      name                    = "rule_we_do not_care_about"
      source_address_prefixes = ["some_other_ip"]
    }
  ]
}

resource "azurerm_network_security_group" "sg_fail2" {
  # this will fail DoNotUseInlineRule
  name                = "sg-fail"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"

  security_rule = [
    {
      name                    = "rule_we_care_about"
      source_address_prefixes = ["disallowed_ip"]
    },
    {
      name                    = "rule_we_do not_care_about2"
      source_address_prefixes = ["allowed_ip"]
    }
  ]
}