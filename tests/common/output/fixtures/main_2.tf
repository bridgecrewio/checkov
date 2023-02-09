resource "aws_s3_bucket" "destination_3" {
  # checkov:skip=CKV_AWS_19: no encryption needed
  bucket = "tf-test-bucket-destination-12345"
  acl = var.acl
  versioning {
    enabled = var.is_enabled
  }
}

resource "aws_s3_bucket" "destination_2" {
  # checkov:skip=CKV_AWS_19: no encryption needed
  bucket = "tf-test-bucket-destination-12345"
  acl = var.acl
  versioning {
    enabled = var.is_enabled
  }
}
