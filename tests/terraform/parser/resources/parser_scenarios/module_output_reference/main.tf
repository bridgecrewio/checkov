module "common" {
  source = "./common"
}
module "bucket" {
  source = "./bucket"
  tags = module.common.tags   # <-- reference to other module, must be resolved in second pass
}