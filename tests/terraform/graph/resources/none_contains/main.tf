variable "iterator" {}

resource "azurerm_key_vault" "kv" {

  dynamic "network_acls" {
    for_each = []
    content {
      default_action             = "Deny"
      bypass                     = ""
      ip_rules                   = null
      virtual_network_subnet_ids = null
    }
  }

  location            = ""
  name                = ""
  resource_group_name = ""
  sku_name            = ""
  tenant_id           = ""
}