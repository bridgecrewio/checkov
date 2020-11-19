variable "name" {}

locals {
  BUCKET_NAME = var.name
}

resource "aws_s3_bucket" "example" {
  bucket = local.BUCKET_NAME
}