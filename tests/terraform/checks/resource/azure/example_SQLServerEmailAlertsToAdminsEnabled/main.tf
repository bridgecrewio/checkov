terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "5.3.0"
    }
  }
}

module "enabled" {
  source       = "./modules/mssql-server"
  admin_alerts = true
}

module "disabled" {
  source       = "./modules/mssql-server"
  admin_alerts = false
}
