# PASS case: "network_profile.network_plugin = azure" 

resource "azurerm_kubernetes_cluster" "pass" {
  name                = "pudpasscluster"
  location            = azurerm_resource_group.pudaksclus.location
  resource_group_name = azurerm_resource_group.pudaksclus.name
  dns_prefix          = "pudaks"
  node_resource_group = "pudaksclus"
  default_node_pool {
    type           = "AvailabilitySet"
    name           = "default"
    node_count     = 3
    vm_size        = "Standard_D2_v2"
    vnet_subnet_id = azurerm_subnet.dep-subnet-pudakssubnet.id
  }
  identity {
    type = "SystemAssigned"
  }
  network_profile {
    network_plugin = "azure"
  }
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.pudaksclus.id
  }
  http_application_routing_enabled  = false
  role_based_access_control_enabled = true
}

# FAIL case 1: "network_profile.network_plugin" not equals to 'azure'

resource "azurerm_kubernetes_cluster" "fail_1" {
  name                = "pudpasscluster"
  location            = azurerm_resource_group.pudaksclus.location
  resource_group_name = azurerm_resource_group.pudaksclus.name
  dns_prefix          = "pudaks"
  node_resource_group = "pudaksclus"
  default_node_pool {
    type           = "AvailabilitySet"
    name           = "default"
    node_count     = 3
    vm_size        = "Standard_D2_v2"
    vnet_subnet_id = azurerm_subnet.dep-subnet-pudakssubnet.id
  }
  identity {
    type = "SystemAssigned"
  }
  network_profile {
    network_plugin = "kubernet"
  }
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.pudaksclus.id
  }
  http_application_routing_enabled  = false
  role_based_access_control_enabled = true
}

# FAIL case 2: "network_profile.network_plugin" does not exist

# If "network_profile" block is absent, by default the value is taken as 'kubernet
# FMI: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/kubernetes_cluster#network_profile

resource "azurerm_kubernetes_cluster" "fail_2" {
  name                = "pudpasscluster"
  location            = azurerm_resource_group.pudaksclus.location
  resource_group_name = azurerm_resource_group.pudaksclus.name
  dns_prefix          = "pudaks"
  node_resource_group = "pudaksclus"
  default_node_pool {
    type           = "AvailabilitySet"
    name           = "default"
    node_count     = 3
    vm_size        = "Standard_D2_v2"
    vnet_subnet_id = azurerm_subnet.dep-subnet-pudakssubnet.id
  }
  identity {
    type = "SystemAssigned"
  }
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.pudaksclus.id
  }
  http_application_routing_enabled  = false
  role_based_access_control_enabled = true
}