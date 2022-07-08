# pass

resource "aws_s3_bucket" "enabled" {
  bucket = "example"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket" "enabled_var" {
  bucket = "example"

  versioning {
    enabled = var.versioning_enabled
  }
}

resource "aws_s3_bucket" "unknown_var" {
  bucket = "example"

  versioning {
    enabled = var.unknown_var
  }
}

variable "unknown_var" {
  description = "unknown value"
}


variable "versioning_enabled" {
  default = true
}

resource "aws_s3_bucket" "legacy_syntax" {
  bucket = "example"

  versioning {
    enabled = "${var.unknown_var}"
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

resource "aws_s3_bucket" "legacy_syntax_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_versioning" "legacy_syntax_v4" {
  bucket = aws_s3_bucket.legacy_syntax_v4.id

  versioning_configuration {
    status = "${var.whatever}"
  }
}
