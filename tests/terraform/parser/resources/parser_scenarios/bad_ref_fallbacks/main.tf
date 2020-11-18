locals {
  BAD_VAR = var.var_not_there
  BAD_LOCAL = local.local_not_there
  BAD_MODULE = module.module_not_there.nope
  BAD_MODULE2 = module.module_not_there
  BAD_MODULE3 = module.module_not_there.nope.still_not
}