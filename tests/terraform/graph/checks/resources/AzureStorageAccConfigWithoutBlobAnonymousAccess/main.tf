variable "rg-name" {
  default = "pud-bc-rg"
}

variable "location" {
  default = "northeurope"
}

# Case 1: Pass: allow_nested_items_to_be_public = False

resource "azurerm_storage_account" "pass" {
  name                     = "pud-storage2023abc1"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  allow_nested_items_to_be_public = false

  tags = {
    bc_status = "pass"
  }
}

# Case 2: Fail: allow_nested_items_to_be_public does NOT exist

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

# Case 3: Fail: allow_nested_items_to_be_public = True

resource "azurerm_storage_account" "fail_2" {
  name                     = "pud-storage2023abc3"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  allow_nested_items_to_be_public = true


  tags = {
    bc_status = "fail_2"
  }
}