locals {
  BUCKET_NAME = "my-bucket-name"
}

resource "aws_s3_bucket" "test_with_locals" {
  bucket = local.BUCKET_NAME
}
