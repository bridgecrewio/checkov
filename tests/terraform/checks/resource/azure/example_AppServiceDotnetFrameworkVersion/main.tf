
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


resource "azurerm_windows_web_app" "pass" {
  #checkov:skip=CKV_AZURE_16: AD might not be required
  name                = var.name
  location            = var.location
  resource_group_name = var.rg_name
  service_plan_id     = var.service_plan_id

  https_only = true
  logs {
    detailed_error_messages = true
    failed_request_tracing  = true
    http_logs {
      file_system {
        retention_in_days = 4
        retention_in_mb   = 25
      }

    }
  }

  storage_account {
    name         = var.storage.name
    type         = var.storage.store_type
    account_name = var.storage.account_name
    share_name   = var.storage.share_name
    access_key   = var.storage.access_key
    mount_path   = var.storage.mount_path
  }

  site_config {
    ftps_state        = "FtpsOnly"
    http2_enabled     = true
    health_check_path = var.health_check_path
    application_stack {
      dotnet_version = "v8.0"
    }
  }


  client_certificate_enabled = true

  auth_settings {
    enabled = true
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_windows_web_app" "fail" {
  #checkov:skip=CKV_AZURE_16: AD might not be required
  name                = var.name
  location            = var.location
  resource_group_name = var.rg_name
  service_plan_id     = var.service_plan_id

  https_only = true
  logs {
    detailed_error_messages = true
    failed_request_tracing  = true
    http_logs {
      file_system {
        retention_in_days = 4
        retention_in_mb   = 25
      }

    }
  }

  storage_account {
    name         = var.storage.name
    type         = var.storage.store_type
    account_name = var.storage.account_name
    share_name   = var.storage.share_name
    access_key   = var.storage.access_key
    mount_path   = var.storage.mount_path
  }

  site_config {
    ftps_state        = "FtpsOnly"
    http2_enabled     = true
    health_check_path = var.health_check_path
    application_stack {
      dotnet_version = "v2.0"
    }
  }


  client_certificate_enabled = true

  auth_settings {
    enabled = true
  }

  identity {
    type = "SystemAssigned"
  }
}


resource "azurerm_windows_web_app" "ignore" {
  #checkov:skip=CKV_AZURE_16: AD might not be required
  name                = var.name
  location            = var.location
  resource_group_name = var.rg_name
  service_plan_id     = var.service_plan_id

  https_only = true
  logs {
    detailed_error_messages = true
    failed_request_tracing  = true
    http_logs {
      file_system {
        retention_in_days = 4
        retention_in_mb   = 25
      }

    }
  }

  storage_account {
    name         = var.storage.name
    type         = var.storage.store_type
    account_name = var.storage.account_name
    share_name   = var.storage.share_name
    access_key   = var.storage.access_key
    mount_path   = var.storage.mount_path
  }

  site_config {
    ftps_state        = "FtpsOnly"
    http2_enabled     = true
    health_check_path = var.health_check_path
  }


  client_certificate_enabled = true

  auth_settings {
    enabled = true
  }

  identity {
    type = "SystemAssigned"
  }
}