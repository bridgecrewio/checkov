# pass

resource "azurerm_postgresql_flexible_server" "pass" {
  name                   = "example-psqlflexibleserver"
  resource_group_name    = "azurerm_resource_group.example.name"
  location               = "azurerm_resource_group.example.location"
  version                = "12"
  delegated_subnet_id    = "azurerm_subnet.example.id"
  private_dns_zone_id    = "azurerm_private_dns_zone.example.id"
  administrator_login    = "psqladmin"
  administrator_password = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
  zone                   = "1"

  storage_mb                   = 32768
  geo_redundant_backup_enabled = true

  sku_name   = "GP_Standard_D4s_v3"
  depends_on = ["azurerm_private_dns_zone_virtual_network_link.example"]

}

# fail

resource "azurerm_postgresql_flexible_server" "fail1" {
  name                   = "example-psqlflexibleserver"
  resource_group_name    = "azurerm_resource_group.example.name"
  location               = "azurerm_resource_group.example.location"
  version                = "12"
  delegated_subnet_id    = "azurerm_subnet.example.id"
  private_dns_zone_id    = "azurerm_private_dns_zone.example.id"
  administrator_login    = "psqladmin"
  administrator_password = "H@Sh1CoR3!"
  zone                   = "1"

  storage_mb                   = 32768
  geo_redundant_backup_enabled = false

  sku_name   = "GP_Standard_D4s_v3"
  depends_on = ["azurerm_private_dns_zone_virtual_network_link.example"]

}

resource "azurerm_postgresql_flexible_server" "fail2" {
  name                   = "example-psqlflexibleserver"
  resource_group_name    = "azurerm_resource_group.example.name"
  location               = "azurerm_resource_group.example.location"
  version                = "12"
  delegated_subnet_id    = "azurerm_subnet.example.id"
  private_dns_zone_id    = "azurerm_private_dns_zone.example.id"
  administrator_login    = "psqladmin"
  administrator_password = "H@Sh1CoR3!"
  zone                   = "1"

  storage_mb = 32768

  sku_name   = "GP_Standard_D4s_v3"
  depends_on = ["azurerm_private_dns_zone_virtual_network_link.example"]

}

# unknown: replica
resource "azurerm_postgresql_flexible_server" "replica" {
  count               = var.replica_count
  name                = "${local.database_name}-replica-${count.index}"
  resource_group_name = var.resource_group.name
  location            = var.resource_group.location
  delegated_subnet_id = var.shared.subnet_id
  private_dns_zone_id = var.shared.dns_zone.id
  sku_name            = var.sku_name
  storage_mb          = var.storage_mb
  version             = var.postgresql_version

  # replication
  create_mode      = "Replica"  # <-- This makes the server a replica.
  source_server_id = azurerm_postgresql_flexible_server.primary.id

  tags = local.standard_tags
  lifecycle {
    precondition {
      condition     = !startswith(var.sku_name, "B_")
      error_message = "Replicas are not supported for burstable SKUs."
    }
    ignore_changes = [
      zone,
      high_availability.0.standby_availability_zone,
      tags
    ]
  }
}


