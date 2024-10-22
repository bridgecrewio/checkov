resource "azurerm_key_vault" "this" {
    name = var.kv_properties.name
    network_acls {
        bypass = var.kv_properties.nacl.bypass
        default_action = var.kv_properties.nacl.default_action
        ip_rules = var.kv_properties.nacl.ip_rules
        virtual_network_subnet_ids = var.kv_properties.nacl.virtual_network_subnet_ids
    }
}

variable "kv_properties" {
  type = object({
    name = string
    nacl = object({
        bypass = string
        default_action = string
        ip_rules = list(string)
        virtual_network_subnet_ids = list(string)
    })
  })
  default = {
    name = "checkov_test"
    nacl = {
      bypass = "AzureServices"
      default_action = "Deny"
      ip_rules = []
      virtual_network_subnet_ids = []
    }
  }
}
