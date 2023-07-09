# pass

resource "azurerm_kubernetes_cluster" "enabled" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"
  dns_prefix          = "example"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  api_server_authorized_ip_ranges = ["192.168.0.0/16"]
}

resource "azurerm_kubernetes_cluster" "private" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"
  dns_prefix          = "example"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  private_cluster_enabled = true
}

resource "azurerm_kubernetes_cluster" "version_3_39" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"
  dns_prefix          = "example"

  api_server_access_profile {
    authorized_ip_ranges = ["192.168.0.0/16"]
  }
}

# fail

resource "azurerm_kubernetes_cluster" "default" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"
  dns_prefix          = "example"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_kubernetes_cluster" "empty" {
  name                = "example"
  location            = "azurerm_resource_group.example.location"
  resource_group_name = "azurerm_resource_group.example.name"
  dns_prefix          = "example"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  api_server_authorized_ip_ranges = []
}
