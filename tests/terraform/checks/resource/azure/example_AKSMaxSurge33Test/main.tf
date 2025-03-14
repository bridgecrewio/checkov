resource "azurerm_kubernetes_cluster" "fail" {
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
    vm_size                      = "Standard_D2_v2"
    enable_auto_scaling          = true
    upgrade_settings {
      max_surge = "34%"
    }
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "fail" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  upgrade_settings {
      max_surge = "34%"
  }
  tags = {
    Environment = "Production"
  }
}

resource "azurerm_kubernetes_cluster" "good1" {
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
    vm_size                      = "Standard_D2_v2"
    enable_auto_scaling          = true
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "good1" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  tags = {
    Environment = "Production"
  }
}

resource "azurerm_kubernetes_cluster" "good2" {
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
    vm_size                      = "Standard_D2_v2"
    enable_auto_scaling          = true
    upgrade_settings {
      max_surge = "33%"
    }
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "good2" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  upgrade_settings {
      max_surge = "33%"
  }
  tags = {
    Environment = "Production"
  }
}