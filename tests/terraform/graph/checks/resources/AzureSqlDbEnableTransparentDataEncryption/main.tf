# FAIL case:   transparent_data_encryption_enabled = false

resource "azurerm_mssql_database" "fail" {
  name                                = "vul-sqldb-1"
  server_id                           = azurerm_mssql_server.dev-sqlserv.id
  transparent_data_encryption_enabled = false
  sku_name                            = "DW100c"
}

# PASS case 1: transparent_data_encryption_enabled = true

resource "azurerm_mssql_database" "pass_1" {
  name                                = "nvul-sqldb-2"
  server_id                           = azurerm_mssql_server.dev-sqlserv.id
  transparent_data_encryption_enabled = true
}

# PASS case 2: Default is 'true'

resource "azurerm_mssql_database" "pass_2" {
  name      = "nvul-sqldb-5"
  server_id = azurerm_mssql_server.dev-sqlserv.id
}
