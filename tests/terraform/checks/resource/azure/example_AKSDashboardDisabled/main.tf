resource "azurerm_kubernetes_cluster" "fail2" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Production"
  }

  addon_profile {
    kube_dashboard {
      enabled = true
    }
  }
}


resource "azurerm_kubernetes_cluster" "fail" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"
  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }
  identity {
    type = "SystemAssigned"
  }
  agent_pool_profile              = ""
  service_principal               = ""
  api_server_authorized_ip_ranges = ["192.168.0.0/16"]
  tags                            = { "Environment" : "Production" }
  addon_profile {
    kube_dashboard { enabled = true }
    oms_agent {
      enabled                    = true
      log_analytics_workspace_id = ""
    }
  }
}



resource "azurerm_kubernetes_cluster" "pass" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"
  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }
  identity {
    type = "SystemAssigned"
  }
  agent_pool_profile {}
  service_principal {}

  api_server_authorized_ip_ranges = ""
  role_based_access_control {
    enabled = true
  }
  network_profile {
    network_plugin = "azure"
  }
  tags = { "Environment" = "Production" }

}

resource "azurerm_kubernetes_cluster" "pass2" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"
  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
    identity {
      type = "SystemAssigned"
    }
    agent_pool_profile = {}
    service_principal  = ""
    role_based_access_control {
      enabled = false
    }
    addon_profile {
      kube_dashboard {
        enabled = false
      }
    }
    network_profile {
      network_plugin = "azure"
    }
  }
  network_policy = "network_policy"
  tags           = { "Environment" : "Production" }
}

