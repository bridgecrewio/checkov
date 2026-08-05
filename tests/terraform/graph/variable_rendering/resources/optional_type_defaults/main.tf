provider "azurerm" {
  features {}
}

variable "keys" {
  type = list(object({
    name = string
    type = optional(string, "RSA-HSM")
    size = optional(number, 2048)
  }))
  default = [{
    name = "examplekey"
  }]
}

variable "config" {
  type = object({
    name   = string
    region = optional(string, "us-east-1")
    port   = optional(number, 443)
  })
  default = {
    name = "myconfig"
  }
}

data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "this" {
  name     = "example-rg"
  location = "West Europe"
}

resource "azurerm_key_vault" "this" {
  name                = "examplekv"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku_name            = "standard"
}

resource "azurerm_key_vault_key" "this" {
  for_each     = { for key in var.keys : key.name => key }
  name         = each.value.name
  key_vault_id = azurerm_key_vault.this.id
  key_type     = each.value.type
  key_size     = each.value.size
  key_opts = [
    "decrypt",
    "encrypt"
  ]
}

resource "aws_instance" "direct_ref" {
  ami           = var.config.region
  instance_type = var.config.port
}

# 3-level nesting: object -> object -> object with optionals at the deepest level
variable "infra" {
  type = object({
    key_vault = object({
      key = object({
        name     = string
        key_type = optional(string, "RSA-HSM")
        key_size = optional(number, 2048)
      })
    })
  })
  default = {
    key_vault = {
      key = {
        name = "deep-key"
      }
    }
  }
}

resource "azurerm_key_vault_key" "nested_ref" {
  name         = var.infra.key_vault.key.name
  key_vault_id = azurerm_key_vault.this.id
  key_type     = var.infra.key_vault.key.key_type
  key_size     = var.infra.key_vault.key.key_size
  key_opts     = ["decrypt", "encrypt"]
}
