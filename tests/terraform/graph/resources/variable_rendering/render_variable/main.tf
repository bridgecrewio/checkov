resource "aws_s3_bucket" "template_bucket" {
  region        = var.region
  bucket        = "test_bucket_name"
  acl           = "acl"
  force_destroy = true
}