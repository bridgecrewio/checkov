### Regression test for https://github.com/bridgecrewio/checkov/issues/4874
### optional() defaults in variable type constraints must be resolved.

provider "azurerm" {
  features {}
}

# --- Scenario 1: for_each with optional() defaults (the original issue) ---

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

# PASS: key_type resolves to "RSA-HSM" via optional() default
resource "azurerm_key_vault_key" "foreach_pass" {
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

# --- Scenario 2: explicit non-HSM value should still fail ---

variable "bad_keys" {
  type = list(object({
    name = string
    type = optional(string, "RSA")
    size = optional(number, 2048)
  }))
  default = [{
    name = "badkey"
  }]
}

# FAIL: key_type resolves to "RSA" (not HSM) via optional() default
resource "azurerm_key_vault_key" "foreach_fail" {
  for_each     = { for key in var.bad_keys : key.name => key }
  name         = each.value.name
  key_vault_id = azurerm_key_vault.this.id
  key_type     = each.value.type
  key_size     = each.value.size
  key_opts = [
    "decrypt",
    "encrypt"
  ]
}

# --- Scenario 3: 3-level nesting with list(object) -- deepest optional triggers PASS ---
# L1: object, L2: object, L3: list(object({key_type = optional(string, "RSA-HSM")}))

variable "infra" {
  type = object({
    key_vault = object({
      keys = list(object({
        name     = string
        key_type = optional(string, "RSA-HSM")
        key_size = optional(number, 2048)
      }))
    })
  })
  default = {
    key_vault = {
      keys = [{
        name = "deep-key"
      }]
    }
  }
}

# PASS: key_type resolved to "RSA-HSM" from optional inside list(object) at L3
resource "azurerm_key_vault_key" "nested_pass" {
  for_each     = { for k in var.infra.key_vault.keys : k.name => k }
  name         = each.value.name
  key_vault_id = azurerm_key_vault.this.id
  key_type     = each.value.key_type
  key_size     = each.value.key_size
  key_opts     = ["decrypt", "encrypt"]
}

# --- Scenario 4: 3-level nesting with map(object), non-HSM default -> FAIL ---
# L1: map(object), L2: object, L3: optional fields

variable "vault_map" {
  type = map(object({
    settings = object({
      key_name = string
      key_type = optional(string, "RSA")
      key_size = optional(number, 2048)
    })
  }))
  default = {
    primary = {
      settings = {
        key_name = "bad-deep-key"
      }
    }
  }
}

# FAIL: key_type resolved to "RSA" (not HSM) via map(object) -> object -> optional
resource "azurerm_key_vault_key" "nested_fail" {
  for_each     = var.vault_map
  name         = each.value.settings.key_name
  key_vault_id = azurerm_key_vault.this.id
  key_type     = each.value.settings.key_type
  key_size     = each.value.settings.key_size
  key_opts     = ["decrypt", "encrypt"]
}
