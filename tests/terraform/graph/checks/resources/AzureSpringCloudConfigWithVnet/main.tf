# PASS case: SKU not B0 and "service_runtime_subnet_id" exists
resource "azurerm_spring_cloud_service" "pass" {
  name                = var.sc_service_name 
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_name            = "S0"
  
  network {
    app_subnet_id                   = "/subscriptions/${var.subscription}/resourceGroups/${var.azurespringcloudvnetrg}/providers/Microsoft.Network/virtualNetworks/${var.vnet_spoke_name}/subnets/${var.app_subnet_id}"
    service_runtime_subnet_id       = "/subscriptions/${var.subscription}/resourceGroups/${var.azurespringcloudvnetrg}/providers/Microsoft.Network/virtualNetworks/${var.vnet_spoke_name}/subnets/${var.service_runtime_subnet_id}"
    cidr_ranges                     = var.sc_cidr
  }
  
  timeouts {
      create = "60m"
      delete = "2h"
  }

  depends_on = [azurerm_resource_group.sc_corp_rg]
  tags = var.tags
  
}

# Fail case 1: If SKU = Basic tier

resource "azurerm_spring_cloud_service" "fail_1" {
  name                = var.sc_service_name 
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_name            = "B0"
  
  network {
    app_subnet_id                   = "/subscriptions/${var.subscription}/resourceGroups/${var.azurespringcloudvnetrg}/providers/Microsoft.Network/virtualNetworks/${var.vnet_spoke_name}/subnets/${var.app_subnet_id}"
    service_runtime_subnet_id       = "/subscriptions/${var.subscription}/resourceGroups/${var.azurespringcloudvnetrg}/providers/Microsoft.Network/virtualNetworks/${var.vnet_spoke_name}/subnets/${var.service_runtime_subnet_id}"
    cidr_ranges                     = var.sc_cidr
  }
  
  timeouts {
      create = "60m"
      delete = "2h"
  }

  depends_on = [azurerm_resource_group.sc_corp_rg]
  tags = var.tags
  
}

#  FAIL case 2: "service_runtime_subnet_id" does not exist

resource "azurerm_spring_cloud_service" "fail_2" {
  name                = var.sc_service_name 
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_name            = "S0"
  
  network {
    app_subnet_id                   = "/subscriptions/${var.subscription}/resourceGroups/${var.azurespringcloudvnetrg}/providers/Microsoft.Network/virtualNetworks/${var.vnet_spoke_name}/subnets/${var.app_subnet_id}"
    cidr_ranges                     = var.sc_cidr
  }
  
  timeouts {
      create = "60m"
      delete = "2h"
  }

  depends_on = [azurerm_resource_group.sc_corp_rg]
  tags = var.tags
  
}