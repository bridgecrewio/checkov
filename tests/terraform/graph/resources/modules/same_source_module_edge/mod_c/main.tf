variable "default_action" {
  type    = string
  default = "Deny"
}

variable "ref" {
  default = null
}

resource "azurerm_storage_account" "sa" {
  network_rules {
    default_action = var.default_action
  }
}
