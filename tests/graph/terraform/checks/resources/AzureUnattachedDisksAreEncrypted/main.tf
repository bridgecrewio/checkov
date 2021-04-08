resource "azurerm_resource_group" "group" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_managed_disk" "managed_disk_good_1" {
  name                 = "acctestmd"
  location             = "West US 2"
  resource_group_name  = azurerm_resource_group.group.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "1"

  encryption_settings {
    enabled = true
  }
  tags = {
    environment = "staging"
  }
}

resource "azurerm_managed_disk" "managed_disk_good_2" {
  name                 = "acctestmd"
  location             = "West US 2"
  resource_group_name  = azurerm_resource_group.group.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "1"
  disk_encryption_set_id = "12345"
  tags = {
    environment = "staging"
  }
}

resource "azurerm_managed_disk" "managed_disk_good_3" {
  name                 = "acctestmd"
  location             = "West US 2"
  resource_group_name  = azurerm_resource_group.group.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "1"
  tags = {
    environment = "staging"
  }

  encryption_settings {
    enabled = true
  }
}

resource "azurerm_managed_disk" "managed_disk_bad_1" {
  name                 = "acctestmd"
  location             = "West US 2"
  resource_group_name  = azurerm_resource_group.group.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "1"
  tags = {
    environment = "staging"
  }
}

resource "azurerm_managed_disk" "managed_disk_bad_2" {
  name                 = "acctestmd"
  location             = "West US 2"
  resource_group_name  = azurerm_resource_group.group.name
  storage_account_type = "Standard_LRS"
  create_option        = "Empty"
  disk_size_gb         = "1"
  encryption_settings {
    enabled = false
  }
  tags = {
    environment = "staging"
  }
}

resource "azurerm_virtual_machine" "virtual_machine_good_1" {
  name                  = "$vm"
  location              = "location"
  resource_group_name  = azurerm_resource_group.group.name
  network_interface_ids = ["id"]
  vm_size               = "Standard_DS1_v2"
  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_id = azurerm_managed_disk.managed_disk_good_1.id
  }
}

resource "azurerm_virtual_machine" "virtual_machine_good_2" {
  name                  = "$vm"
  location              = "location"
  resource_group_name  = azurerm_resource_group.group.name
  network_interface_ids = ["id"]
  vm_size               = "Standard_DS1_v2"
  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_id = azurerm_managed_disk.managed_disk_good_2.id
  }
}


resource "azurerm_virtual_machine" "virtual_machine_good_3" {
  name                  = "$vm"
  location              = "location"
  resource_group_name  = azurerm_resource_group.group.name
  network_interface_ids = ["id"]
  vm_size               = "Standard_DS1_v2"
  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "managed"
  }
}


resource "azurerm_virtual_machine" "virtual_machine_bad_1" {
  name                  = "$vm"
  location              = "location"
  resource_group_name  = azurerm_resource_group.group.name
  network_interface_ids = ["id"]
  vm_size               = "Standard_DS1_v2"
  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = azurerm_managed_disk.managed_disk_bad_1.id
  }
}

resource "azurerm_virtual_machine" "virtual_machine_bad_2" {
  name                  = "$vm"
  location              = "location"
  resource_group_name  = azurerm_resource_group.group.name
  network_interface_ids = ["id"]
  vm_size               = "Standard_DS1_v2"
  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = azurerm_managed_disk.managed_disk_bad_2.id
  }
}