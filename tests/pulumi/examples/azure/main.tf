terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "4.81.0" }
  }
}

provider "azurerm" {
  features {}
  subscription_id                 = "00000000-0000-0000-0000-000000000000"
  resource_provider_registrations = "none"
}

resource "azurerm_resource_group" "rg" {
  name     = "checkov-rg"
  location = "eastus"
}

resource "azurerm_storage_account" "insecureStorage" {
  name                            = "insecurestorage01"
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = "eastus"
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_0"
  allow_nested_items_to_be_public = true
  https_traffic_only_enabled      = false
}

resource "azurerm_storage_account" "secureStorage" {
  name                            = "securestorage01"
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = "eastus"
  account_tier                    = "Standard"
  account_replication_type        = "GRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false
  shared_access_key_enabled       = false
  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }
  queue_properties {
    logging {
      delete                = true
      read                  = true
      write                 = true
      version               = "1.0"
      retention_policy_days = 10
    }
  }
}

resource "azurerm_network_security_group" "nsg" {
  name                = "open-nsg"
  resource_group_name = azurerm_resource_group.rg.name
  location            = "eastus"
  security_rule {
    name                       = "ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_key_vault" "vault" {
  name                = "checkov-kv"
  resource_group_name = azurerm_resource_group.rg.name
  location            = "eastus"
  tenant_id           = "00000000-0000-0000-0000-000000000000"
  sku_name            = "standard"
}
