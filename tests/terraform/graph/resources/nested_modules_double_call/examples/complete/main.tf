provider "aws" {
  region = var.region
}

module "s3_user" {
  source        = "../../"
  namespace     = var.namespace
  stage         = var.stage
  name          = var.name
  force_destroy = true
  s3_actions    = var.s3_actions
  s3_resources  = var.s3_resources
}
