
resource "azurerm_app_service" "fail2" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  storage_account {
    name         = "test_name"
    type         = "AzureBlob"
    account_name = "test_account_name"
    share_name   = "test_share_name"
    access_key   = "test_access_key"
  }
}

resource "azurerm_app_service" "pass" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  storage_account {
    name         = "test_name"
    type         = "AzureFiles"
    account_name = "test_account_name"
    share_name   = "test_share_name"
    access_key   = "test_access_key"
  }
}

resource "azurerm_app_service" "fail" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  site_config {
    scm_type = "someValue"
  }
}

resource "azurerm_linux_web_app" "pass" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  https_only          = true
  site_config {
    http2_enabled = true
  }
  identity {
    type = "SystemAssigned"

  }
  site_config {
    minimum_tls_version = "1.2"
  }
  storage_account {
    name         = "test_name"
    type         = "AzureFiles"
    account_name = "test_account_name"
    share_name   = "test_share_name"
    access_key   = "test_access_key"
  }
}

resource "azurerm_linux_web_app" "fail" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id

  site_config {
    http2_enabled       = false
    minimum_tls_version = "1.1"
  }


}

resource "azurerm_windows_web_app" "pass" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id
  https_only          = true
  site_config {
    http2_enabled       = true
    minimum_tls_version = "1.2"
  }
  identity {
    type = "SystemAssigned"
  }
  storage_account {
    name         = "test_name"
    type         = "AzureFiles"
    account_name = "test_account_name"
    share_name   = "test_share_name"
    access_key   = "test_access_key"
  }
}

resource "azurerm_windows_web_app" "fail" {
  name                = "example"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_service_plan.example.location
  service_plan_id     = azurerm_service_plan.example.id

  site_config {
    http2_enabled       = false
    minimum_tls_version = "1.1"
  }
}