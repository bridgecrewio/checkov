resource "aws_s3_bucket" "inner_s3" {
  bucket = "tf-test-bucket-destination-12345"
  acl = ""
  versioning {
    enabled = var.versioning
  }
}