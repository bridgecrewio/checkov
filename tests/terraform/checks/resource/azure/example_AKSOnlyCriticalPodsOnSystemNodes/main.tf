resource "azurerm_kubernetes_cluster" "pass" {
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
    only_critical_addons_enabled = true
  }
}

resource "azurerm_kubernetes_cluster" "fail1" {
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
  }
}

resource "azurerm_kubernetes_cluster" "fail2" {
  name                      = "example"
  
  default_node_pool {
    name                         = "defaultpool"
    only_critical_addons_enabled = false
  }
}

resource "azurerm_kubernetes_cluster" "fail3" {
  name                      = "example"
  
}

resource "azurerm_kubernetes_cluster" "fail4" {
  name                         = "example"
  only_critical_addons_enabled = true
  
}

