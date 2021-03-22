
resource "azurerm_virtual_machine" "example_ok" {
  name                  = "${var.prefix}-vm"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  network_interface_ids = [azurerm_network_interface.main.id]
  vm_size               = "Standard_DS1_v2"
}

resource "azurerm_backup_protected_vm" "vm_protected_backup" {
  resource_group_name = azurerm_resource_group.example_ok.name
  recovery_vault_name = azurerm_recovery_services_vault.example_ok.name
  source_vm_id        = azurerm_virtual_machine.example_ok.id
  backup_policy_id    = azurerm_backup_policy_vm.example_ok.id
}


resource "azurerm_virtual_machine" "example_not_ok" {
  name                  = "${var.prefix}-vm"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  network_interface_ids = [azurerm_network_interface.main.id]
  vm_size               = "Standard_DS1_v2"
}
