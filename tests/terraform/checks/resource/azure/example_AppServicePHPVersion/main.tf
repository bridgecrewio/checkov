
            resource "azurerm_app_service" "fail" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                php_version = "7.4"
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
                php_version = "8.1"
                scm_type                 = "someValue"
                }
              }

            resource "azurerm_app_service" "pass2" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                scm_type                 = "someValue"
                }
              }
