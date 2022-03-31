resource "azurerm_storage_account" "fail1" {
  allow_blob_public_access = true
}

resource "azurerm_storage_account" "fail2" {
  allow_blob_public_access = "true"
}

resource "azurerm_storage_account" "fail3" {

}

resource "azurerm_storage_account" "pass1" {
  allow_blob_public_access = false
}

resource "azurerm_storage_account" "pass2" {
  allow_blob_public_access = "false"
}