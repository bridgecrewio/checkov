locals {
  bucket = var.bucket
}

module "inner_module" {
  source = "../inner_module"
  bucket = local.bucket
}
