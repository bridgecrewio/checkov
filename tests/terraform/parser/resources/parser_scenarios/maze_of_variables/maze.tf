
variable "gratuitous_var_default" {
  type = string
  default = "-yay"
}

variable "input" {
  default = "module-input"
}

locals {
  BUCKET = "bucket"
  NAME = {
    "module-input-bucket" = "mapped-${local.BUCKET}-name"
  }
  TAIL = "works"
}


module "bucket" {
  source   = "./bucket"
  name     = var.input
}

resource "aws_s3_bucket" "example2" {
  #             resolves to: mapped-bucket-name
  #             |            resolves to: module-input-bucket
  #             |            |                              resolves to: works
  #             |            |                              |           resolves to: -yay
  #             |            |                              |           |
  #             v            v                              v           v
  bucket = "${local.NAME[${module.bucket.bucket_name}]}-${local.TAIL}${var.gratuitous_var_default}"
  # final result: mapped-bucket-name-works-yay
}