module "b" {
  source = "./mod_a"
}

module "a" {
  source = "./mod_a"
  result = module.b.result
}

module "c" {
  source = "./mod_c"

  default_action = "Deny"

  ref = module.b.result.some_attr
}
