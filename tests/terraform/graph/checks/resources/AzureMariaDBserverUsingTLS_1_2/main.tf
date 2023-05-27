
resource "azurerm_mariadb_server" "pass_1" {
  name                = "pud-mariadb-server"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name

  administrator_login          = "dbadmin123"
  administrator_login_password = "M@r!@D3" # checkov:skip=CKV_SECRET_80 test secret

  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_2"
}

# This case passes as ssl_minimal_tls_version_enforced will default to TLS1_2

resource "azurerm_mariadb_server" "pass_2" {
  name                = "pud-mariadb-server"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name

  administrator_login          = "dbadmin123"
  administrator_login_password = "M@r!@D3" # checkov:skip=CKV_SECRET_80 test secret

  ssl_enforcement_enabled          = true

}

resource "azurerm_mariadb_server" "fail_1" {
  name                = "pud-mariadb-server"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name

  administrator_login          = "dbadmin123"
  administrator_login_password = "M@r!@D3" # checkov:skip=CKV_SECRET_80 test secret

}

resource "azurerm_mariadb_server" "fail_2" {
  name                = "pud-mariadb-server"
  location            = azurerm_resource_group.pud_rg.location
  resource_group_name = azurerm_resource_group.pud_rg.name

  administrator_login          = "dbadmin123"
  administrator_login_password = "M@r!@D3" # checkov:skip=CKV_SECRET_80 test secret

  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_1"

}
