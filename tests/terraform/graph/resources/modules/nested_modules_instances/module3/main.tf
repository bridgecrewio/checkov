locals {
  bucket2 = var.bucket2
}

resource "aws_s3_bucket" "var_bucket" {
  bucket                  = local.bucket2
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
