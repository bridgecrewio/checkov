locals {
  instances = {
    vm01 = {
      size = "Standard_B2ms"
    }
  }

  common_tags = {
    team = "platform"
    os   = "Windows"
  }
}

module "vm" {
  for_each = local.instances
  source   = "./mod"

  name    = each.key
  size    = each.value.size
  vm_role = "testing"
  tags    = local.common_tags
}
