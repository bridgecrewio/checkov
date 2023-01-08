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
  }

  identity {
    type = "SystemAssigned"
  }


  tags                    = var.tags
  local_account_disabled  = var.local_account_disabled
  private_cluster_enabled = var.private_cluster
}

resource "azurerm_kubernetes_cluster" "failed_empty_max_pods" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = var.default_node_pool.name
    node_count = var.default_node_pool.node_count
    vm_size    = var.default_node_pool.vm_size
    max_pods   = []
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
  }

  identity {
    type = "SystemAssigned"
  }


  tags                    = var.tags
  local_account_disabled  = var.local_account_disabled
  private_cluster_enabled = var.private_cluster
}

resource "azurerm_kubernetes_cluster" "fail2" {
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

resource "azurerm_kubernetes_cluster_node_pool" "pass" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  max_pods              = 51
  tags = {
    Environment = "Production"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "fail" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  max_pods              = 33
  tags = {
    Environment = "Production"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "fail2" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  tags = {
    Environment = "Production"
  }
}