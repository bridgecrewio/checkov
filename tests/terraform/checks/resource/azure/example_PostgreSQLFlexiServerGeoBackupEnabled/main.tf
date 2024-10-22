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


