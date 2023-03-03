
resource "azurerm_spring_cloud_api_portal" "fail" {
  name                          = "default"
  spring_cloud_service_id       = azurerm_spring_cloud_service.example.id
  gateway_ids                   = [azurerm_spring_cloud_gateway.example.id]
  public_network_access_enabled = true
  instance_count                = 1
  sso {
    client_id     = "test"
    client_secret = "secret"
    issuer_uri    = "https://www.example.com/issueToken"
    scope         = ["read"]
  }
}

resource "azurerm_spring_cloud_api_portal" "fail2" {
  name                          = "default"
  spring_cloud_service_id       = azurerm_spring_cloud_service.example.id
  gateway_ids                   = [azurerm_spring_cloud_gateway.example.id]
  https_only_enabled            = false
  public_network_access_enabled = true
  instance_count                = 1
  sso {
    client_id     = "test"
    client_secret = "secret"
    issuer_uri    = "https://www.example.com/issueToken"
    scope         = ["read"]
  }
}

resource "azurerm_spring_cloud_api_portal" "pass" {
  name                          = "default"
  spring_cloud_service_id       = azurerm_spring_cloud_service.example.id
  gateway_ids                   = [azurerm_spring_cloud_gateway.example.id]
  https_only_enabled            = true
  public_network_access_enabled = true
  instance_count                = 1
  sso {
    client_id     = "test"
    client_secret = "secret"
    issuer_uri    = "https://www.example.com/issueToken"
    scope         = ["read"]
  }
}