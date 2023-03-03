subnet_list = [
  {
    name           = "dynamic_subnet1"
    address_prefix = "10.100.1.0/24"
    security_group = "azurerm_network_security_group.dynamic_nsg_pass.id"
  },
  {
    name           = "dynamic_subnet2"
    address_prefix = "10.100.2.0/24"
    security_group = "azurerm_network_security_group.dynamic_nsg_pass.id"
  },
  {
    name           = "dynamic_subnet3"
    address_prefix = "10.100.3.0/24"
    security_group = "azurerm_network_security_group.dynamic_nsg_pass.id"
  }
]

fail_nsg_rules = [
  {
    name                       = "AllowHttpIn"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  },
  {
    name                       = "AllowHttpsIn"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  },
  {
    name                       = "AllowRdpIn"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  },
  {
    name                       = "AllowIcmpIn"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Icmp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
]


pass_nsg_rules = [
  {
    name                       = "DenyHttpIn"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  },
  {
    name                       = "AllowHttpsIn"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "35.181.123.80/32"
    destination_address_prefix = "*"
  },
  {
    name                       = "DenyRdpIn"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  },
  {
    name                       = "DenyIcmpIn"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Icmp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
]