# PASS case 1: If "account_kind" is not mentioned, it equals to "StorageV2"
# Reference: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account#account_kind

resource "azurerm_storage_account" "pass_1" {
  name                     = "pud_store_acc"
  resource_group_name      = azurerm_resource_group.pud_rg.name
  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  blob_properties {
    delete_retention_policy {
      days = 10
    }
  }

}

# PASS case 2: If "blob_properties.delete_retention_policy.days" is not mentioned, it defaults to 7 days
# Reference: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account#days

resource "azurerm_storage_account" "pass_2" {
  name                     = "pud_store_acc"
  resource_group_name      = azurerm_resource_group.pud_rg.name
  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "BlobStorage"

  blob_properties {
    delete_retention_policy {
    
    }
  }

}

# FAIL case 1: "account_kind" should NOT equal to "FileStorage"

resource "azurerm_storage_account" "fail_1" {
  name                     = "pud_store_acc"
  resource_group_name      = azurerm_resource_group.pud_rg.name
  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "FileStorage" 

  blob_properties {
    delete_retention_policy {
      days = 10
    }
  }

}

# FAIL case 2: "delete_retention_policy" block is not defined

resource "azurerm_storage_account" "fail_2" {
  name                     = "pud_store_acc"
  resource_group_name      = azurerm_resource_group.pud_rg.name
  location                 = azurerm_resource_group.pud_rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  blob_properties {
    
  }

}