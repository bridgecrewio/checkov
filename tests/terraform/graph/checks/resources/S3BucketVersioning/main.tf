# pass

resource "aws_s3_bucket" "enabled" {
  bucket = "example"

  versioning {
    enabled = true
  }
}

# fail

resource "aws_s3_bucket" "default" {
  bucket = "example"
}

resource "aws_s3_bucket" "disabled" {
  bucket = "example"

  versioning {
    enabled = false
  }
}

# provider version 4

resource "aws_s3_bucket" "enabled_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_versioning" "enabled_v4" {
  bucket = aws_s3_bucket.enabled_v4.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "disabled_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_versioning" "disabled_v4" {
  bucket = aws_s3_bucket.disabled_v4.id

  versioning_configuration {
    status = "Suspended"
  }
}
