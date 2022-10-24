# pass

resource "azurerm_linux_virtual_machine" "disabled" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "linux-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  allow_extension_operations = false
}

resource "azurerm_windows_virtual_machine" "disabled" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "win-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  allow_extension_operations = false
}

# fail

resource "azurerm_linux_virtual_machine" "default" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "linux-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}

resource "azurerm_linux_virtual_machine" "enabled" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "linux-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  allow_extension_operations = true
}

resource "azurerm_windows_virtual_machine" "default" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "win-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
}

resource "azurerm_windows_virtual_machine" "enabled" {
  admin_password      = "admin"
  admin_username      = "admin123"
  location            = "azurerm_resource_group.test.location"
  name                = "win-vm"
  resource_group_name = "azurerm_resource_group.test.name"
  size                = "Standard_F2"

  network_interface_ids = [
    "azurerm_network_interface.test.id"
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  allow_extension_operations = true
}
