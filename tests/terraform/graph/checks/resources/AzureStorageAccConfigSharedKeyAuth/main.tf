variable "rg-name" {
  default = "pud-bc-rg"
}

variable "location" {
  default = "northeurope"
}

# Case 1: Pass: shared_access_key_enabled = False

resource "azurerm_storage_account" "pass" {
  name                     = "pud-storage2023abc1"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = false

  tags = {
    bc_status = "pass"
  }
}

# Case 2: Fail: shared_access_key_enabled does NOT exist

resource "azurerm_storage_account" "fail_1" {
  name                     = "pud-storage2023abc2"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    bc_status = "fail_1"
  }
}

# Case 3: Fail: shared_access_key_enabled = True

resource "azurerm_storage_account" "fail_2" {
  name                     = "pud-storage2023abc3"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = true


  tags = {
    bc_status = "fail_2"
  }
}