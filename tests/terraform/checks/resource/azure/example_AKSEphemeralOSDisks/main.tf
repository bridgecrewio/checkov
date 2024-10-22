resource "azurerm_kubernetes_cluster" "pass" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1

  default_node_pool {
    name = "default"

    enable_host_encryption       = true
    vm_size                      = "Standard_E4ads_v5"
    os_disk_type                 = "Ephemeral"
    zones                        = [1, 2, 3]
    only_critical_addons_enabled = true

    type                 = "VirtualMachineScaleSets"
    vnet_subnet_id       = var.subnet_id
    enable_auto_scaling  = true
    max_count            = 6
    min_count            = 2
    orchestrator_version = local.kubernetes_version
  }

}

resource "azurerm_kubernetes_cluster" "fail" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1

  tags = {
    Environment = "Production"
  }

  default_node_pool {
    name = "default"

    enable_host_encryption       = true
    vm_size                      = "Standard_E4ads_v5"
    zones                        = [1, 2, 3]
    only_critical_addons_enabled = true

    type                 = "VirtualMachineScaleSets"
    vnet_subnet_id       = var.subnet_id
    enable_auto_scaling  = true
    max_count            = 6
    min_count            = 2
    orchestrator_version = local.kubernetes_version
  }
  
}

resource "azurerm_kubernetes_cluster" "fail2" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  os_disk_type          = "Managed"

  tags = {
    Environment = "Production"
  }

  default_node_pool {
    name = "default"

    enable_host_encryption       = true
    vm_size                      = "Standard_E4ads_v5"
    os_disk_type                 = "Managed"
    zones                        = [1, 2, 3]
    only_critical_addons_enabled = true

    type                 = "VirtualMachineScaleSets"
    vnet_subnet_id       = var.subnet_id
    enable_auto_scaling  = true
    max_count            = 6
    min_count            = 2
    orchestrator_version = local.kubernetes_version
  }
  

}