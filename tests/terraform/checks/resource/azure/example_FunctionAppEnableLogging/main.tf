resource "azurerm_function_app" "fail" {
  name                       = "test-azure-functions"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  https_only                 = false
  enable_builtin_logging     = false #default is true

  site_config {
    dotnet_framework_version = "v4.0"
    scm_type                 = "LocalGit"
    min_tls_version          = 1.1
    ftps_state               = "AllAllowed"
    http2_enabled            = false
    cors {
      allowed_origins = ["*"]
    }
  }
}

resource "azurerm_function_app" "pass" {
  name                       = "test-azure-functions"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  https_only                 = false

  site_config {
    dotnet_framework_version = "v4.0"
    scm_type                 = "LocalGit"
    min_tls_version          = 1.1
    ftps_state               = "AllAllowed"
    http2_enabled            = false
    cors {
      allowed_origins = ["*"]
    }
  }
}

resource "azurerm_function_app" "pass2" {
  name                       = "test-azure-functions"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  https_only                 = false
  enable_builtin_logging     = true

  site_config {
    dotnet_framework_version = "v4.0"
    scm_type                 = "LocalGit"
    min_tls_version          = 1.1
    ftps_state               = "AllAllowed"
    http2_enabled            = false
    cors {
      allowed_origins = ["*"]
    }
  }
}

resource "azurerm_function_app_slot" "fail" {
  name                       = "test-azure-functions-slot"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  function_app_name          = azurerm_function_app.example.name
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  enable_builtin_logging     = false
  site_config {
    http2_enabled = false
  }
  auth_settings {
    enabled = false
  }
}

resource "azurerm_function_app_slot" "pass" {
  name                       = "test-azure-functions-slot"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  function_app_name          = azurerm_function_app.example.name
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  site_config {
    http2_enabled = false
  }
  auth_settings {
    enabled = false
  }
}

resource "azurerm_function_app_slot" "pass2" {
  name                       = "test-azure-functions-slot"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  function_app_name          = azurerm_function_app.example.name
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  enable_builtin_logging     = true
  site_config {
    http2_enabled = false
  }
  auth_settings {
    enabled = false
  }
}