resource "aws_s3_bucket" "destination" {
  bucket = "tf-test-bucket-destination-12345"
  acl = var.acl
  versioning {
    enabled = var.is_enabled
  }
}