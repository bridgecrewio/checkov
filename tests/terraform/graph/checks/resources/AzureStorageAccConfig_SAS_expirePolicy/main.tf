variable "rg-name" {
  default = "pud-bc-rg"
}

variable "location" {
  default = "northeurope"
}

# Case 1: Pass: shared_access_key_enabled = false AND sas_policy exists

resource "azurerm_storage_account" "pass" {
  name                     = "pud-storage2023abc1"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = false

  sas_policy {
    expiration_period = "90.00:00:00"
    expiration_action = "Log"
  }

  tags = {
    bc_status = "pass"
  }
}

# Case 2: Fail: None of the arguments exist

resource "azurerm_storage_account" "fail_1" {
  name                     = "pud-storage2023abc2"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# Case 3: FAIL: shared_access_key_enabled is True and sas_policy.expiration_period is empty

resource "azurerm_storage_account" "fail_2" {
  name                     = "pud-storage2023abc3"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = true

  sas_policy {
    expiration_period = ""

  }

}

# Case 4: FAIL: shared_access_key_enabled is False but sas_policy.expiration_period is empty

resource "azurerm_storage_account" "fail_3" {
  name                     = "pud-storage2023abc4"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = false

  sas_policy {
    expiration_period = ""
  }

}

# Case 4: FAIL: shared_access_key_enabled is True

resource "azurerm_storage_account" "fail_4" {
  name                     = "pud-storage2023abc4"
  resource_group_name      = var.rg-name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  shared_access_key_enabled = true

  sas_policy {
    expiration_period = "90.00:00:00"
  }

}