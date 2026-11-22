resource "aws_s3_bucket" "pass" {
  bucket = "bucket_good"
}


resource "aws_s3_bucket_lifecycle_configuration" "pass" {
  bucket = aws_s3_bucket.pass.id
  rule {
    id     = ""
    status = ""
  }
}

resource "aws_s3_bucket" "fail" {
  bucket = "bucket_bad_1"
}

# provider v3

resource "aws_s3_bucket" "pass_v3" {
  bucket = "bucket_good"

  lifecycle_rule {
    id                                     = "Delete old incomplete multi-part uploads"
    enabled                                = true
    abort_incomplete_multipart_upload_days = 7
  }
}

# count-based resources

variable "create_bucket" {
  default = true
}

resource "aws_s3_bucket" "pass_count" {
  count  = var.create_bucket ? 1 : 0
  bucket = "bucket_with_count"
}

resource "aws_s3_bucket_lifecycle_configuration" "pass_count" {
  count  = var.create_bucket ? 1 : 0
  bucket = aws_s3_bucket.pass_count[0].id

  rule {
    id     = "expire-old-objects"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}
