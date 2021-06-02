resource "aws_s3_bucket" "test-bucket1" {
  bucket = "test-bucket1"
  # checkov:skip=CKV_AWS_20: The bucket is a public static content host
  acl    = "public-read"
  lifecycle_rule {
    id      = "90 Day Lifecycle"
    enabled = true
    expiration {
      days = 90
    }
    noncurrent_version_expiration {
      days = 90
    }
    abort_incomplete_multipart_upload_days = 90
  }
  provider = aws.current_region
}