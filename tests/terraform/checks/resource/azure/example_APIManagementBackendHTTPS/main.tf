resource "azurerm_api_management_backend" "pass" {
  name                = "example-pike"
  resource_group_name = azurerm_resource_group.example.name
  api_management_name = azurerm_api_management.example.name
  protocol            = "http"
  url                 = "https://backend"
}

resource "azurerm_api_management_backend" "fail" {
  name                = "example-backend"
  resource_group_name = azurerm_resource_group.example.name
  api_management_name = azurerm_api_management.example.name
  protocol            = "http"
  url                 = "http://backend"
}

resource "azurerm_api_management_backend" "unknown_var" {
  protocol = "http"
  url      = var.backend_url
}

resource "azurerm_api_management_backend" "unknown_each" {
  protocol = "http"
  url      = each.value.backend_url
}

resource "azurerm_api_management_backend" "unknown_local" {
  protocol = "http"
  url      = local.backend_url
}

resource "azurerm_api_management_backend" "unknown_missing_url" {
  protocol = "http"
}
