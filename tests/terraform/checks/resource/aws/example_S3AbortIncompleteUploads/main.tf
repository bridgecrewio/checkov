# fail

resource "aws_s3_bucket_lifecycle_configuration" "fail" {
  # Must have bucket versioning enabled first
  depends_on = [aws_s3_bucket_versioning.versioning]

  bucket = aws_s3_bucket.versioning_bucket.id

  rule {
    id = "config"

    filter {
      prefix = "config/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 60
      storage_class   = "GLACIER"
    }

    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "fail2" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    id = "log"

    expiration {
      days = 90
    }

    filter {
      and {
        prefix = "log/"

        tags = {
          rule      = "log"
          autoclean = "true"
        }
      }
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }

  rule {
    id = "tmp"

    filter {
      prefix = "tmp/"
    }

    expiration {
      date = "2023-01-13T00:00:00Z"
    }

    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "fail3" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    id = "log"

    status = "Disabled"
  }
}

# pass

resource "aws_s3_bucket_lifecycle_configuration" "pass2" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    id = "log"

    expiration {
      days = 90
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "id-2"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "pass" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    id = "log"

    expiration {
      days = 90
    }

    filter {
      and {
        prefix = "log/"

        tags = {
          rule      = "log"
          autoclean = "true"
        }
      }
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }
  }

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    id = "tmp"

    expiration {
      date = "2023-01-13T00:00:00Z"
    }

    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "pass3" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
    filter {}
    id = "log"
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "resource_with_dynamic_rule_pass4" {
  bucket = aws_s3_bucket.main.bucket

  rule {
    id     = "abort_incomplete_multipart_upload"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = var.config.abort_incomplete_multipart_upload
    }
  }

  dynamic "rule" {
    for_each = local.lifecycle_rules.storage_class

    content {
      id     = "storage_class_is_${var.config.storage_class}"
      status = "Enabled"

      transition {
        storage_class = var.config.storage_class
      }
    }
  }
}