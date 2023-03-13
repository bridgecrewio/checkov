# PASS case

resource "azurerm_subnet" "pass" {
  name                                           = "pass"
  resource_group_name                            = azurerm_resource_group.pud_rg.name
  virtual_network_name                           = azurerm_virtual_network.pud_vnet.name
  address_prefixes                               = ["192.0.8.0/24"]
  enforce_private_link_endpoint_network_policies = true
  enforce_private_link_service_network_policies  = true
  delegation {
    name = "Microsoft.Web/serverFarms"
    service_delegation {
      name = "Microsoft.Web/serverFarms"
    }
  }
}

resource "azurerm_network_security_group" "pass" {
  name                = "pass"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  security_rule {
    name                       = "default"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "pass" {
  subnet_id                 = azurerm_subnet.pass.id
  network_security_group_id = azurerm_network_security_group.pass.id
}

# FAIL case 1: service_delegation should not be equal to Microsoft.Netapp/volumes

resource "azurerm_subnet" "fail_1" {
  name                                           = "fail_1"
  resource_group_name                            = azurerm_resource_group.pud_rg.name
  virtual_network_name                           = azurerm_virtual_network.pud_vnet.name
  address_prefixes                               = ["192.0.8.0/24"]
  enforce_private_link_endpoint_network_policies = true
  enforce_private_link_service_network_policies  = true
  delegation {
    name = "Microsoft.Netapp/volumes"
    service_delegation {
      name = "Microsoft.Netapp/volumes"
    }
  }
}

resource "azurerm_network_security_group" "fail_1" {
  name                = "fail_1"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  security_rule {
    name                       = "default"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "fail_1" {
  subnet_id                 = azurerm_subnet.fail_1.id
  network_security_group_id = azurerm_network_security_group.fail_1.id
}

# FAIL case 2: azurerm_subnet name should not be AZUREFIREWALLSUBNET/GatewaySubnet

resource "azurerm_subnet" "fail_2" {
  name                                           = "AzureFirewallSubnet"
  resource_group_name                            = azurerm_resource_group.pud_rg.name
  virtual_network_name                           = azurerm_virtual_network.pud_vnet.name
  address_prefixes                               = ["192.0.8.0/24"]
  enforce_private_link_endpoint_network_policies = true
  enforce_private_link_service_network_policies  = true
  delegation {
    name = "Microsoft.Web/serverFarms"
    service_delegation {
      name = "Microsoft.Web/serverFarms"
    }
  }
}

resource "azurerm_network_security_group" "fail_2" {
  name                = "fail_2"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name
  security_rule {
    name                       = "default"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "fail_2" {
  subnet_id                 = azurerm_subnet.fail_2.id
  network_security_group_id = azurerm_network_security_group.fail_2.id
}


# FAIL case 3: Subnet not associated to NSG resource OR NSG resource doesn't exist

resource "azurerm_subnet" "fail_3" {
  name                 = "fail_3"
  resource_group_name  = azurerm_resource_group.dep-rg-j1-1-rlp-1473.name
  virtual_network_name = azurerm_virtual_network.dep-vn-j1-2-rlp-1473.name
  address_prefixes     = ["10.0.17.0/24"]
}
