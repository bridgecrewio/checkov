## SHOULD PASS: Min nodes set to 0
resource "azurerm_machine_learning_compute_cluster" "ckv_unittest_pass" {
  name                          = "example"
  location                      = "West Europe"
  vm_priority                   = "LowPriority"
  vm_size                       = "Standard_DS2_v2"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.example.id
  subnet_resource_id            = azurerm_subnet.example.id

  scale_settings {
    min_node_count                       = 0
    max_node_count                       = 1
    scale_down_nodes_after_idle_duration = "PT30S" # 30 seconds
  }
}

## SHOULD FAIL: Min nodes set to 1
resource "azurerm_machine_learning_compute_cluster" "ckv_unittest_fail" {
  name                          = "example"
  location                      = "West Europe"
  vm_priority                   = "LowPriority"
  vm_size                       = "Standard_DS2_v2"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.example.id
  subnet_resource_id            = azurerm_subnet.example.id

  scale_settings {
    min_node_count                       = 1
    max_node_count                       = 2
    scale_down_nodes_after_idle_duration = "PT30S" # 30 seconds
  }
}