
resource "azurerm_app_service" "fail" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  site_config {
    dotnet_framework_version = "v5.0"
    scm_type                 = "someValue"
    }
  }


resource "azurerm_app_service" "pass" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  site_config {
    dotnet_framework_version = "v6.0"
    scm_type                 = "someValue"
    }
  }

resource "azurerm_app_service" "ignore" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  site_config {
    java_version = "11"
    java_container = "Tomcat"
    java_container_version = 10.0
    http2_enabled = true
    ftps_state ="FtpsOnly"
    }
  }
