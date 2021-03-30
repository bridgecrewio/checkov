locals {
  bucket_name          = "test_bucket_name"
}

resource "aws_s3_bucket" "template_bucket" {
  region        = "us-west-2"
  bucket        = local.bucket_name
  acl           = "acl"
  force_destroy = true
}

