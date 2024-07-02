# pass

resource "azurerm_storage_account" "default" {
  name                     = "storageaccountname"
  resource_group_name      = "azurerm_resource_group.example.name"
  location                 = "azurerm_resource_group.example.location"
  account_tier             = "Standard"
  account_replication_type = "GRS"
  #checkov:skip=CKV_AZURE_59,CKV_AZURE_33,CKV_AZURE_44,CKV_AZURE_190,CKV2_AZURE_40,CKV2_AZURE_47,CKV2_AZURE_33,CKV2_AZURE_41,CKV2_AZURE_38
  #checkov:skip=CKV2_AZURE_1,BLA_BLA_BLA
}