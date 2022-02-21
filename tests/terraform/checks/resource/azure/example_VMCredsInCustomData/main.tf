# pass

resource "azurerm_virtual_machine" "no_secret" {
  name                  = "${var.prefix}-vm"
  location              = ""
  network_interface_ids = []
  resource_group_name   = ""
  vm_size               = ""
  storage_os_disk {
    create_option = ""
    name          = ""
  }

  os_profile {
    admin_username = "example"
    computer_name  = "hostname"
    custom_data    = <<EOF
example
EOF
  }
}

resource "azurerm_virtual_machine" "no_custom_data" {
  name                  = "${var.prefix}-vm"
  location              = ""
  network_interface_ids = []
  resource_group_name   = ""
  vm_size               = ""
  storage_os_disk {
    create_option = ""
    name          = ""
  }

  os_profile {
    admin_username = "example"
    computer_name  = "hostname"
  }
}

resource "azurerm_virtual_machine" "empty_os_profile" {
  name                  = "${var.prefix}-vm"
  location              = ""
  network_interface_ids = []
  resource_group_name   = ""
  vm_size               = ""
  storage_os_disk {
    create_option = ""
    name          = ""
  }

  os_profile = [] # just for a test
}

resource "azurerm_virtual_machine" "no_os_profile" {
  name                  = "${var.prefix}-vm"
  location              = ""
  network_interface_ids = []
  resource_group_name   = ""
  vm_size               = ""
  storage_os_disk {
    create_option = ""
    name          = ""
  }
}

# fail

resource "azurerm_virtual_machine" "secret" {
  name                  = "${var.prefix}-vm"
  location              = ""
  network_interface_ids = []
  resource_group_name   = ""
  vm_size               = ""
  storage_os_disk {
    create_option = ""
    name          = ""
  }

  os_profile {
    admin_username = "example"
    computer_name  = "hostname"
    custom_data    = <<EOF
0000-0000-0000-0000-000000000000
EOF
  }
}