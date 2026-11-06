locals {
  common_tags = {
    team = "platform"
    env  = "non-prod"
  }

  instances = {
    vm01 = {
      location = "uksouth"
      size     = "Standard_B2ms"
      zone     = "1"
      tags = merge(local.common_tags, {
        Role = "testing"
        os   = "Windows"
      })
    }
  }
}

module "vm" {
  for_each = local.instances
  source   = "./mod"

  name     = each.key
  location = each.value.location
  size     = each.value.size
  zone     = each.value.zone
  tags     = each.value.tags
}
