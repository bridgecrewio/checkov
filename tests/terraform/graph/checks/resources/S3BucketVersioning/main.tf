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

# Reference by name
variable "bucket_name" {
}

resource "aws_s3_bucket" "ref_by_name" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "aws_bucket_versioning" {
  bucket = var.bucket_name
  versioning_configuration {
    status = "Enabled"
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



locals {
  prefix = "kevin-code-sec"
  buckets = [
    "test-code-sec-a",
    "test-code-sec-b",
  ]
  test_buckets = [
    "test-bucket1",
    "test-bucket2"
  ]
  additional_tags = {
    Env                  = "DEV"
    Point_of_Contact     = "CloudSec"
    Managed_by_Terraform = true
  }
}

resource "aws_s3_bucket" "this" {
  for_each = toset(local.test_buckets)
  bucket   = "${local.prefix}-${each.key}"
  tags     = local.additional_tags
}


resource "aws_s3_bucket_versioning" "this" {
  for_each = toset(local.test_buckets)
  bucket = aws_s3_bucket.this[each.key].id

  versioning_configuration {
    status = "Enabled"}
}
