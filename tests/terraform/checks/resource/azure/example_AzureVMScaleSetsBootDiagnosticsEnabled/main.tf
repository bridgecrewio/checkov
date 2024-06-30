data "pud_test" "pud_test" {}

# Pass 1: 'boot_diagnostics' argument is present in this IaC

resource "azurerm_windows_virtual_machine_scale_set" "pass_1" {
  name                 = "pud-vmss"
  resource_group_name  = data.pud_test
  location             = data.pud_test
  sku                  = "Standard_F2"
  instances            = 1
  admin_password       = data.pud_test
  admin_username       = data.pud_test
  computer_name_prefix = "pudvm-"

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2016-Datacenter-Server-Core"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = data.pud_test
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = data.pud_test
    }
  }

  boot_diagnostics {
    storage_account_uri = ""
  }
}

# Pass 2: 'boot_diagnostics' argument is present in this IaC

resource "azurerm_linux_virtual_machine_scale_set" "pass_2" {
  name                = "example-vmss"
  resource_group_name = data.pud_test
  location            = data.pud_test
  sku                 = "Standard_F2"
  instances           = 1
  admin_username      = "adminuser"

  admin_ssh_key {
    username   = data.pud_test
    public_key = data.pud_test
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = "pud-nic"
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = data.pud_test
    }
  }

  boot_diagnostics {
    storage_account_uri = ""
  }
}

# Fail 1: 'boot_diagnostics' argument is NOT present in this IaC

resource "azurerm_windows_virtual_machine_scale_set" "fail_1" {
  name                 = "pud-vmss"
  resource_group_name  = data.pud_test
  location             = data.pud_test
  sku                  = "Standard_F2"
  instances            = 1
  admin_password       = data.pud_test
  admin_username       = data.pud_test
  computer_name_prefix = "pudvm-"

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2016-Datacenter-Server-Core"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = data.pud_test
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = data.pud_test
    }
  }
}

# Fail 2: 'boot_diagnostics' argument is NOT present in this IaC

resource "azurerm_linux_virtual_machine_scale_set" "fail_2" {
  name                = "example-vmss"
  resource_group_name = data.pud_test
  location            = data.pud_test
  sku                 = "Standard_F2"
  instances           = 1
  admin_username      = "adminuser"

  admin_ssh_key {
    username   = data.pud_test
    public_key = data.pud_test
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  network_interface {
    name    = "pud-nic"
    primary = true

    ip_configuration {
      name      = "internal"
      primary   = true
      subnet_id = data.pud_test
    }
  }
}

