# pass

resource "azurerm_network_security_rule" "https" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = 443
  source_address_prefix  = "Internet"
}

resource "azurerm_network_security_rule" "rdp_restricted_prefixes" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = 3389
  source_address_prefixes = [
    "123.123.123.123/32",
    "10.0.0.0/16"
  ]
}

resource "azurerm_network_security_group" "rdp_restricted" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"

  security_rule {
    name      = "example"
    access    = "Allow"
    direction = "Inbound"
    priority  = 100
    protocol  = "Tcp"

    destination_port_range = 3389
    source_address_prefix  = "10.0.0.0/16"
  }
}

# fail

resource "azurerm_network_security_rule" "rdp" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range  = 3389
  source_address_prefix   = "*"
  destination_port_ranges = null
  source_address_prefixes = null
}

resource "azurerm_network_security_rule" "all" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = "*"
  source_address_prefix  = "Internet"
}

resource "azurerm_network_security_rule" "range" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = "3000-4000"
  source_address_prefix  = "Internet"
}

resource "azurerm_network_security_rule" "ranges_prefixes" {
  name                        = "example"
  access                      = "Allow"
  direction                   = "Inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "Tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = null
  source_address_prefix  = null
  destination_port_ranges = [
    3389,
    443
  ]
  source_address_prefixes = [
    "Internet",
    "10.0.0.0/16"
  ]
}

resource "azurerm_network_security_group" "ranges" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"

  security_rule {
    name      = "example"
    access    = "Allow"
    direction = "Inbound"
    priority  = 100
    protocol  = "Tcp"

    destination_port_ranges = [
      "3000-4000",
      "8000-9000"
    ]
    source_address_prefix = "*"
  }
}

# lower case

resource "azurerm_network_security_rule" "ranges_prefixes_lower_case" {
  name                        = "example"
  access                      = "allow"
  direction                   = "inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = null
  source_address_prefix  = null
  destination_port_ranges = [
    3389,
    443
  ]
  source_address_prefixes = [
    "internet",
    "10.0.0.0/16"
  ]
}

resource "azurerm_network_security_rule" "range_prefix_lower_case" {
  name                        = "example"
  access                      = "allow"
  direction                   = "inbound"
  network_security_group_name = "azurerm_network_security_group.example.name"
  priority                    = 100
  protocol                    = "tcp"
  resource_group_name         = "azurerm_resource_group.example.name"

  destination_port_range = "3000-4000"
  source_address_prefix  = "internet"
}

resource "azurerm_network_security_group" "snet_nsgs" {
  count               = length(local.subnets)
  name                = "${local.root}-snet-${lookup(local.subnets[count.index], "name")}-nsg"
  location            = azurerm_resource_group.net_rg.location
  resource_group_name = azurerm_resource_group.net_rg.name
  tags                = local.tags


  dynamic "security_rule" {
    for_each = [for s in local.subnets[count.index].nsg_rules : {
      name                       = s.name
      priority                   = s.priority
      direction                  = s.direction
      access                     = s.access
      protocol                   = s.protocol
      source_port_range          = s.source_port_range
      destination_port_range     = s.destination_port_range
      source_address_prefix      = s.source_address_prefix
      destination_address_prefix = s.destination_address_prefix
      description                = s.description
    }]
    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
      description                = security_rule.value.description
    }
  }
}
