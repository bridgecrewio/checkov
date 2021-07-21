module "submodule1" {
  source = "../submodule1"
  v = var.v
}

module "submodule2" {
  source = "../submodule2"
  v = var.v
}