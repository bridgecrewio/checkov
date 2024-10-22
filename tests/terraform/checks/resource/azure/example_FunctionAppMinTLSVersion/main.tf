resource "azurerm_function_app" "fail" {
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

resource "azurerm_function_app_slot" "fail2" {
  name                       = "test-azure-functions_slot"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  function_app_name          = azurerm_function_app.example.name
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  site_config {
    min_tls_version = 1.1
  }
}

resource "azurerm_linux_function_app" "fail3" {
  name                 = "example-linux-function-app"
  resource_group_name  = azurerm_resource_group.example.name
  location             = azurerm_resource_group.example.location
  service_plan_id      = azurerm_service_plan.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.1
  }
}
resource "azurerm_windows_function_app" "fail4" {
  name                = "example-windows-function-app"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  site_config {
    minimum_tls_version = 1.1
  }
}

resource "azurerm_linux_function_app_slot" "fail5" {
  name                 = "example-linux-function-app-slot"
  function_app_id      = azurerm_linux_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.1
  }
}
resource "azurerm_windows_function_app_slot" "fail6" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.1
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

  site_config {
    dotnet_framework_version = "v4.0"
    scm_type                 = "LocalGit"
    min_tls_version          = 1.2
    ftps_state               = "AllAllowed"
    http2_enabled            = false
    cors {
      allowed_origins = ["*"]
    }
  }
}

resource "azurerm_function_app" "pass3" {
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
    min_tls_version          = "1.2"
    ftps_state               = "AllAllowed"
    http2_enabled            = false
    cors {
      allowed_origins = ["*"]
    }
  }
}

resource "azurerm_function_app_slot" "pass4" {
  name                       = "test-azure-functions_slot"
  location                   = azurerm_resource_group.example.location
  resource_group_name        = azurerm_resource_group.example.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  function_app_name          = azurerm_function_app.example.name
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
}

resource "azurerm_linux_function_app" "pass5" {
  name                 = "example-linux-function-app"
  resource_group_name  = azurerm_resource_group.example.name
  location             = azurerm_resource_group.example.location
  service_plan_id      = azurerm_service_plan.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.2
  }
}
resource "azurerm_windows_function_app" "pass6" {
  name                = "example-windows-function-app"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location

  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  site_config {
    minimum_tls_version = 1.2
  }
}

resource "azurerm_linux_function_app_slot" "pass7" {
  name                 = "example-linux-function-app-slot"
  function_app_id      = azurerm_linux_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.2
  }
}
resource "azurerm_windows_function_app_slot" "pass8" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {
    minimum_tls_version = 1.2
  }
}
resource "azurerm_windows_function_app_slot" "pass9" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  site_config {}
}
