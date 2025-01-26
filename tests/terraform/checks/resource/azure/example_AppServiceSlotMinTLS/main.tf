resource "azurerm_app_service_slot" "fail" {
  name                = "brian"
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only = false #thedefault

  site_config {
    dotnet_framework_version = "v4.0"
    min_tls_version          = "1.1"
    remote_debugging_enabled = true
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

#default
resource "azurerm_app_service_slot" "pass" {
  name                = "fred"
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only = false #thedefault


  site_config {
    dotnet_framework_version = "v4.0"
    remote_debugging_enabled = true #default is false
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

resource "azurerm_app_service_slot" "pass2" {
  name                = "ted"
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only = false #thedefault


  site_config {
    dotnet_framework_version = "v4.0"
    min_tls_version          = "1.2" #the default is 1.2
    remote_debugging_enabled = true  #default is false
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

resource "azurerm_app_service_slot" "pass3" {
  name                = "ned"
  app_service_name    = azurerm_app_service.example.name
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  https_only = false #thedefault


  site_config {
    dotnet_framework_version = "v4.0"
    min_tls_version          = "1.3" #the default is 1.2
    remote_debugging_enabled = true  #default is false
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

resource "azurerm_resource_group" "example" {
  name     = "example"
  location = "uksouth"
}

resource "azurerm_app_service_plan" "example" {
  sku {
    tier = "free"
    size = "small"
  }
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  name                = "example"
}

resource "azurerm_app_service" "example" {
  name                = "simon"
  app_service_plan_id = azurerm_app_service_plan.example.id
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
}


provider "azurerm" {
  features {}
}