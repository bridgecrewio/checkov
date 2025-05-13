resource "azurerm_mssql_database" "good1" {
  name           = "example-database"
  server_id      = azurerm_mssql_server.example.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  license_type   = "LicenseIncluded"
  max_size_gb    = 4
  read_scale     = true
  sku_name       = "S0"

  tags = {
    environment = "Production"
  }
}

resource "azurerm_mssql_database" "good2" {
    name                 = "example-database"
    server_id            = azurerm_mssql_server.example.id
    collation            = "SQL_Latin1_General_CP1_CI_AS"
    license_type         = "LicenseIncluded"
    max_size_gb          = 4
    read_scale           = true
    sku_name             = "S0"
    storage_account_type = "Geo"

    tags = {
        environment = "Production"
    }
}

resource "azurerm_mssql_database" "fail" {
    name                 = "example-database"
    server_id            = azurerm_mssql_server.example.id
    collation            = "SQL_Latin1_General_CP1_CI_AS"
    license_type         = "LicenseIncluded"
    max_size_gb          = 4
    read_scale           = true
    sku_name             = "S0"
    storage_account_type = "Local"


    tags = {
        environment = "Production"
    }

}