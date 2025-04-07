provider "azurerm" {
  features {}
}

variable "resource_group_name" {
  description = "resource_group_name"
  type = string
  default = "test"
}

variable "location" {
  description = "Azure location name"
  type = string
  default = "test"
}

resource "azurerm_storage_account" "example" {
  name                     = "test"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "example" {
  name                = "example-appserviceplan"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

resource "azurerm_linux_function_app" "example" {
  name                      = "example-linux-functionapp"
  location                  = var.location
  resource_group_name       = var.resource_group_name
  service_plan_id           = azurerm_app_service_plan.example.id
  storage_account_name      = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  site_config {
    https_only = true
    
  }
}

output "function_app_endpoint" {
  value = azurerm_linux_function_app.example.default_hostname
}