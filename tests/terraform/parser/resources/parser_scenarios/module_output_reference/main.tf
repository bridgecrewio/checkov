module "common" {
  source = "./common"
}
module "bucket" {
  source = "./bucket"
  tags = module.common.tags
}