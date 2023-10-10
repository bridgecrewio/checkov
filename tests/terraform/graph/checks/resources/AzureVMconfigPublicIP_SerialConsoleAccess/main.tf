variable "prefix" {
  default = "pud_bc"
}

variable "pub-ip-id" {
  default = "/subscriptions/61pudrpd-6234-7856-a98e-09pu7dep65h2/resourceGroups/pud-rg/providers/Microsoft.Network/publicIPAddresses/pud-bc-checkov-ip"
}

data "azurerm_network_interface" "pud-id" {
  name                 = "existing"
  resource_group_name  = "pud-rg"
}

resource "azurerm_resource_group" "pud-rg" {
  name     = "${var.prefix}-rg"
  location = "West Europe"
}

# Case 1: Pass case: "ip_configuration.public_ip_address_id" exists

resource "azurerm_network_interface" "pass_int" {
  name                = "pass-nic"
  location            = azurerm_resource_group.pud-rg.location
  resource_group_name = azurerm_resource_group.pud-rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.prefix
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id = var.pub-ip-id
  }
}

resource "azurerm_virtual_machine" "pass_vm" {
  name                  = "${var.prefix}-vm"
  location              = azurerm_resource_group.pud-rg.location
  resource_group_name   = azurerm_resource_group.pud-rg.name
  network_interface_ids = [azurerm_network_interface.pass_int.id]
  vm_size               = "Standard_DS1_v2"
}

# Case 2: Fail case: Missing "ip_configuration.public_ip_address_id" (does NOT exist)

resource "azurerm_network_interface" "fail_int" {
  name                = "fail-nic"
  location            = azurerm_resource_group.pud-rg.location
  resource_group_name = azurerm_resource_group.pud-rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.prefix
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_linux_virtual_machine" "pud-linux-vm" {
  name                = "pud-linux-vm"
  resource_group_name = azurerm_resource_group.pud-rg.name
  location            = azurerm_resource_group.pud-rg.location
  size                = "Standard_F2"
  admin_username      = "pud-admin"
  network_interface_ids = [
    azurerm_network_interface.fail_int.id,
  ]

}