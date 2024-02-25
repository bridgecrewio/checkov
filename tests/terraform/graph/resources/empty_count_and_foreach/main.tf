locals {
  should_use = false
}


resource "azurerm_private_endpoint" "private_endpoint_pod_empty_count" {
  count = local.should_use == true ? 1 : 0
  name = "${azurerm_key_vault.empty_count.name}-test"
  location = azurerm_resource_group.cfg.location
  resource_group_name = azurerm_resource_group.cfg.name
  subnet_id = data.azurerm_subnet.private_end_point_subnet[0].id
  tags = var.tags
  private_service_connection {
    is_manual_connection = false
    name = "${azurerm_key_vault.empty_count.name}-test"
    private_connection_resource_id = azurerm_key_vault.empty_count.id
    subresource_names = ["vault"]
  }
}

resource "azurerm_private_endpoint" "private_endpoint_pod_empty_foreach" {
  for_each = {}
  name = "${azurerm_key_vault.empty_count.name}-test"
  location = azurerm_resource_group.cfg.location
  resource_group_name = azurerm_resource_group.cfg.name
  subnet_id = data.azurerm_subnet.private_end_point_subnet[0].id
  tags = var.tags
  private_service_connection {
    is_manual_connection = false
    name = "${azurerm_key_vault.empty_count.name}-test"
    private_connection_resource_id = azurerm_key_vault.empty_count.id
    subresource_names = ["vault"]
  }
}


resource "azurerm_key_vault" "empty_count" {
  location            = ""
  name                = "test"
  resource_group_name = ""
  sku_name            = ""
  tenant_id           = ""
}