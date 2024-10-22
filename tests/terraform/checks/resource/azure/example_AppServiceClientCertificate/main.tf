
resource "azurerm_app_service" "fail" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
}

resource "azurerm_app_service" "fail2" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  client_cert_enabled = false
}

resource "azurerm_app_service" "pass" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  client_cert_enabled = true
}

resource "azurerm_linux_web_app" "fail" {
  name                       = "example"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_service_plan.example.location
  service_plan_id            = azurerm_service_plan.example.id
  client_certificate_enabled = false
  site_config {}
}

resource "azurerm_linux_web_app" "fail2" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  auth_settings {
    enabled = false
  }
  site_config {}
}

resource "azurerm_linux_web_app" "pass" {
  name                       = "example"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_service_plan.example.location
  service_plan_id            = azurerm_service_plan.example.id
  client_certificate_enabled = true
  auth_settings {
    enabled = true
  }
  site_config {}
}

resource "azurerm_windows_web_app" "fail" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id

  site_config {}
}

resource "azurerm_windows_web_app" "fail2" {
  name                       = "example"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_service_plan.example.location
  service_plan_id            = azurerm_service_plan.example.id
  client_certificate_enabled = false
  auth_settings {
    enabled = false
  }
  site_config {}
}

resource "azurerm_windows_web_app" "pass" {
  name                       = "example"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_service_plan.example.location
  service_plan_id            = azurerm_service_plan.example.id
  client_certificate_enabled = true
  auth_settings {
    enabled = true
  }
  site_config {}
}