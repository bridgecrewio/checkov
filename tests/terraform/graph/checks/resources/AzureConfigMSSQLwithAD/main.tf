# PASS case: "azuread_administrator.login_username" exists

resource "azurerm_mssql_server" "pass" {
  name                         = "mssqlserver"
  resource_group_name          = "pud-bcrew-RG"
  location                     = "azurerm_resource_group.example.location"
  version                      = "12.0"
  administrator_login          = "missadministrator"
  administrator_login_password = "thisIsKat11"
  minimum_tls_version          = "1.2"
    azuread_administrator {
      azuread_authentication_only = true
      login_username = "pud"
      object_id      = "908-au767-098776"
    }

  tags = {
    environment = "prod-01"
  }
}

#FAIL case 1: "azuread_administrator.login_username" doesn't exist

resource "azurerm_mssql_server" "fail_1" {
  name                         = "mssqlserver"
  resource_group_name          = azurerm_resource_group.dep-rg-j1-1-rlp-77266.name
  location                     = azurerm_resource_group.dep-rg-j1-1-rlp-77266.location
  version                      = "12.0"
  administrator_login          = "pudadministrator1"
  administrator_login_password = "thisIspudfortest2"  # checkov:skip=CKV_SECRET_6 test secret
}

# FAIL case 2: "azuread_administrator.login_username" exists

resource "azurerm_mssql_server" "fail_2" {
  name                         = "mssqlserver"
  resource_group_name          = "pud-bcrew-RG"
  location                     = "azurerm_resource_group.example.location"
  version                      = "12.0"
  administrator_login          = "missadministrator"
  administrator_login_password = "thisIsKat11"
  minimum_tls_version          = "1.2"
    azuread_administrator {
      azuread_authentication_only = true
      login_username = " "
      object_id      = "908-au767-098776"
    }

  tags = {
    environment = "prod-01"
  }
}