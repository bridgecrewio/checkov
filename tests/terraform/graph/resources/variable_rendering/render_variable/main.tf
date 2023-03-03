resource "aws_s3_bucket" "template_bucket" {
  region        = var.region
  bucket        = "test_bucket_name"
  acl           = "acl"
  force_destroy = true
}

resource "aws_s3_bucket" "storage_bucket" {
  region        = "us-west-2"
  bucket        = var.bucket_name
  acl           = "acl"
  force_destroy = true
}