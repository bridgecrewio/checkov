resource "azurerm_linux_virtual_machine_scale_set" "pass" {
  name                            = var.scaleset_name
  resource_group_name             = var.resource_group.name
  location                        = var.resource_group.location
  sku                             = var.sku
  instances                       = var.instance_count
  admin_username                  = var.admin_username
  disable_password_authentication = true
  tags                            = { test = "Fail" }
}

resource "azurerm_linux_virtual_machine_scale_set" "fail" {
  name                            = var.scaleset_name
  resource_group_name             = var.resource_group.name
  location                        = var.resource_group.location
  sku                             = var.sku
  instances                       = var.instance_count
  admin_username                  = var.admin_username
  disable_password_authentication = false
  tags                            = { test = "Fail" }
}

resource "azurerm_linux_virtual_machine_scale_set" "pass2" {
  name                = var.scaleset_name
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  sku                 = var.sku
  instances           = var.instance_count
  admin_username      = var.admin_username
  tags                = { test = "Fail" }
}

resource "azurerm_linux_virtual_machine" "pass" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = azurerm_resource_group.test.location
  name                = "linux-vm"
  resource_group_name = azurerm_resource_group.test.name
  size                = "Standard_F2"

  network_interface_ids = [
    azurerm_network_interface.test.id
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}

resource "azurerm_network_interface" "test" {
  location            = "uksouth"
  name                = "test"
  resource_group_name = "test"
  ip_configuration {
    name                          = "jim"
    private_ip_address_allocation = "Dynamic"
  }
}
resource "azurerm_resource_group" "test" {
  location = "uksouth"
  name     = "test"
}
provider "azurerm" {
  features {}
}

resource "azurerm_linux_virtual_machine" "pass2" {
  admin_password                  = "admin"
  admin_username                  = "admin123"
  location                        = azurerm_resource_group.test.location
  name                            = "linux-vm"
  resource_group_name             = azurerm_resource_group.test.name
  size                            = "Standard_F2"
  disable_password_authentication = true
  network_interface_ids = [
    azurerm_network_interface.test.id
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}
resource "azurerm_linux_virtual_machine" "fail" {
  admin_password                  = "admin"
  admin_username                  = "admin123"
  location                        = azurerm_resource_group.test.location
  name                            = "linux-vm"
  resource_group_name             = azurerm_resource_group.test.name
  size                            = "Standard_F2"
  disable_password_authentication = false
  network_interface_ids = [
    azurerm_network_interface.test.id
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}