resource "azurerm_linux_web_app" "test" {
  name                = "acctestWA-%d"
  location            = azurerm_resource_group.test.location
  resource_group_name = azurerm_resource_group.test.name
  service_plan_id     = azurerm_service_plan.test.id

  app_settings = {
    "DOCKER_REGISTRY_SERVER_URL"          = "https://mcr.microsoft.com"
    "DOCKER_REGISTRY_SERVER_USERNAME"     = ""
    "DOCKER_REGISTRY_SERVER_PASSWORD"     = ""
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }

  site_config {
    application_stack {
      docker_image     = "mcr.microsoft.com/appsvc/staticsite"
      docker_image_tag = "latest"
    }
  }
}


resource "azurerm_linux_web_app_slot" "test" {
  name           = "acctestWAS-%d"
  app_service_id = azurerm_linux_web_app.test.id

  app_settings = {
    "DOCKER_REGISTRY_SERVER_URL"          = "https://mcr.microsoft.com"
    "DOCKER_REGISTRY_SERVER_USERNAME"     = ""
    "DOCKER_REGISTRY_SERVER_PASSWORD"     = ""
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }

  site_config {
    application_stack {
      docker_image     = "busybox"
      docker_image_tag = "latest"
    }
  }
}
