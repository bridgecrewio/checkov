
variable "resource_group_name" {
  default = "pud_pgres_rg"
}

variable "location" {
  default = "East US 2"
}

variable "subnet_id" {
  default = "pud-az-subnet"
}

# case 1: PASS: azurerm_private_endpoint exists and is connected

resource "azurerm_postgresql_server" "pass" {
  name                = "pass_pgres_server"
  location            = var.location
  resource_group_name = var.resource_group_name

  administrator_login          = "pud"
  administrator_login_password = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 5120

  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  auto_grow_enabled            = false

  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_2"
}

resource "azurerm_private_endpoint" "pass_priendpt" {
  name                = "pass_priendpt"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.subnet_id

  private_service_connection {
    name                           = "dep-privservcon"
    private_connection_resource_id = azurerm_postgresql_server.pass.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }
}


# case 2: FAIL: azurerm_private_endpoint does not exist

resource "azurerm_postgresql_server" "fail" {
  name                = "fail_pgres_server"
  location            = var.location
  resource_group_name = var.resource_group_name

  administrator_login          = "pud"
  administrator_login_password = "P@ssw0rd@1" # checkov:skip=CKV_SECRET_80 test secret

  sku_name   = "GP_Gen5_4"
  version    = "11"
  storage_mb = 5120

  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  auto_grow_enabled            = false

  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_2"
}