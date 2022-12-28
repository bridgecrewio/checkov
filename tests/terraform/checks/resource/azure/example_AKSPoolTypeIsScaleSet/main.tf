resource "azurerm_kubernetes_cluster" "pass" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = var.default_node_pool.name
    node_count = var.default_node_pool.node_count
    vm_size    = var.default_node_pool.vm_size
    max_pods   = 51
    type       = "VirtualMachineScaleSets"
  }

  identity {
    type = "SystemAssigned"
  }


  tags                    = var.tags
  local_account_disabled  = var.local_account_disabled
  private_cluster_enabled = var.private_cluster
}

resource "azurerm_kubernetes_cluster" "fail" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = var.default_node_pool.name
    node_count = var.default_node_pool.node_count
    vm_size    = var.default_node_pool.vm_size
    max_pods   = 28
    type       = "AvailabilitySet"
  }

  identity {
    type = "SystemAssigned"
  }


  tags                    = var.tags
  local_account_disabled  = var.local_account_disabled
  private_cluster_enabled = var.private_cluster
}

resource "azurerm_kubernetes_cluster" "pass2" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = var.default_node_pool.name
    node_count = var.default_node_pool.node_count
    vm_size    = var.default_node_pool.vm_size
  }

  identity {
    type = "SystemAssigned"
  }


  tags                    = var.tags
  local_account_disabled  = var.local_account_disabled
  private_cluster_enabled = var.private_cluster
}
