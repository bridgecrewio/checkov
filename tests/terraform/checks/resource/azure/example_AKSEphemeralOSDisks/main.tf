resource "azurerm_kubernetes_cluster" "pass" {
  name                  = "internal"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.example.id
  vm_size               = "Standard_DS2_v2"
  node_count            = 1
  os_disk_type          = "Ephemeral"

  tags = {
    Environment = "Production"
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
}