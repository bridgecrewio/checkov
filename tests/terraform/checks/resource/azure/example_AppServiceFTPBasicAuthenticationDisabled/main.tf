resource "azurerm_linux_web_app" "fail1" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  ftp_publish_basic_authentication_enabled = true
  site_config {}
}

resource "azurerm_linux_web_app" "fail2" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  site_config {}
}

resource "azurerm_windows_web_app" "fail1" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  ftp_publish_basic_authentication_enabled = true
  site_config {}
}

resource "azurerm_windows_web_app" "fail2" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  site_config {}
}

resource "azurerm_linux_web_app" "good" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  ftp_publish_basic_authentication_enabled = false

  site_config {}
}

resource "azurerm_windows_web_app" "good" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  ftp_publish_basic_authentication_enabled = false

  site_config {}
}