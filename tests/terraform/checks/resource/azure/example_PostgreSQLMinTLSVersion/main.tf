resource "azurerm_postgresql_server" "fail" {
  name = "fail"

  public_network_access_enabled    = true
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_1"
}


resource "azurerm_postgresql_server" "pass" {
  name = "fail"

  public_network_access_enabled    = true
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_2"
}

resource "azurerm_postgresql_server" "fail2" {
  name = "fail"

  public_network_access_enabled = true
  ssl_enforcement_enabled       = true
}