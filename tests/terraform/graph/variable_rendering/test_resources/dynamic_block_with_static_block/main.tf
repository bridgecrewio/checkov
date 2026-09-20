variable "versioning" {
  type    = bool
  default = true
}

resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = "example"

  rule {
    id     = "abort-incomplete-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  dynamic "rule" {
    for_each = var.versioning ? [1] : []

    content {
      id     = "expire-noncurrent-versions"
      status = "Enabled"

      noncurrent_version_expiration {
        noncurrent_days = 1
      }
    }
  }
}
