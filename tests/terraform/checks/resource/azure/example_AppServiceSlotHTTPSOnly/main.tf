
resource "azurerm_app_service_slot" "fail" {
  name                = random_id.server.hex
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only               = false #thedefault
  min_tls_version          = "1.1" #the default is 1.2
  remote_debugging_enabled = true  #default is false

  site_config {
    dotnet_framework_version = "v4.0"
  }

  app_settings = {
    "SOME_KEY" = "some-value"
  }

  connection_string {
    name  = "Database"
    type  = "SQLServer"
    value = "Server=some-server.mydomain.com;Integrated Security=SSPI"
  }
}


resource "azurerm_linux_web_app_slot" "fail" {
  name           = "fail-slot"
  app_service_id = azurerm_linux_web_app.fail.id
  https_only     = false

  site_config {}
}

resource "azurerm_windows_web_app_slot" "fail" {
  name           = "fail-slot"
  app_service_id = azurerm_windows_web_app.fail.id
  https_only     = false
  
  site_config {}
}


resource "azurerm_app_service_slot" "fail2" {
  name                = random_id.server.hex
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  #  https_only = false #thedefault
  min_tls_version          = "1.1" #the default is 1.2
  remote_debugging_enabled = true  #default is false

  site_config {
    dotnet_framework_version = "v4.0"
  }

  app_settings = {
    "SOME_KEY" = "some-value"
  }

  connection_string {
    name  = "Database"
    type  = "SQLServer"
    value = "Server=some-server.mydomain.com;Integrated Security=SSPI"
  }
}

resource "azurerm_app_service_slot" "pass" {
  name                = random_id.server.hex
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only               = true  #thedefault
  min_tls_version          = "1.1" #the default is 1.2
  remote_debugging_enabled = true  #default is false

  site_config {
    dotnet_framework_version = "v4.0"
  }

  app_settings = {
    "SOME_KEY" = "some-value"
  }

  connection_string {
    name  = "Database"
    type  = "SQLServer"
    value = "Server=some-server.mydomain.com;Integrated Security=SSPI"
  }
}

resource "azurerm_linux_web_app_slot" "pass" {
  name           = "pass-slot"
  app_service_id = azurerm_linux_web_app.pass.id
  https_only     = true

  site_config {}
}

resource "azurerm_windows_web_app_slot" "pass" {
  name           = "pass-slot"
  app_service_id = azurerm_windows_web_app.pass.id
  https_only     = true
  
  site_config {}
}