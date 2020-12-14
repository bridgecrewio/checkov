module "bucket" {
  source   = "./bucket"
}

locals {
  BUCKET_NAME = "${module.bucket.bucket_name}"
}