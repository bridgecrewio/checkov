# pass

resource "azurerm_linux_function_app" "disabled" {
  name                       = "example-linux-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  public_network_access_enabled = false
}

resource "azurerm_linux_function_app_slot" "disabled" {
  name                 = "example-linux-function-app-slot"
  function_app_id      = azurerm_linux_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  public_network_access_enabled = false
}

resource "azurerm_windows_function_app" "disabled" {
  name                       = "example-windows-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  public_network_access_enabled = false
}

resource "azurerm_windows_function_app_slot" "disabled" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  public_network_access_enabled = false
}

# fail

resource "azurerm_linux_function_app" "default" {
  name                       = "example-linux-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id
}

resource "azurerm_linux_function_app_slot" "default" {
  name                 = "example-linux-function-app-slot"
  function_app_id      = azurerm_linux_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name
}

resource "azurerm_windows_function_app" "default" {
  name                       = "example-windows-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id
}

resource "azurerm_windows_function_app_slot" "default" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name
}

resource "azurerm_linux_function_app" "enabled" {
  name                       = "example-linux-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  public_network_access_enabled = true
}

resource "azurerm_linux_function_app_slot" "enabled" {
  name                 = "example-linux-function-app-slot"
  function_app_id      = azurerm_linux_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  public_network_access_enabled = true
}

resource "azurerm_windows_function_app" "enabled" {
  name                       = "example-windows-function-app"
  resource_group_name        = azurerm_resource_group.example.name
  location                   = azurerm_resource_group.example.location
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  service_plan_id            = azurerm_service_plan.example.id

  public_network_access_enabled = true
}

resource "azurerm_windows_function_app_slot" "enabled" {
  name                 = "example-slot"
  function_app_id      = azurerm_windows_function_app.example.id
  storage_account_name = azurerm_storage_account.example.name

  public_network_access_enabled = true
}
