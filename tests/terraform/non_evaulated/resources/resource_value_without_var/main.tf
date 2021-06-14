# pass
resource "aws_s3_bucket" "enabled_bucket" {
  bucket = "enabled_bucket"
  acl    = "private"

  versioning {
    enabled = var.versioning_enabled
  }
}

# fail
resource "aws_s3_bucket" "disabled_bucket" {
  bucket = "disabled_bucket"
  acl    = "private"

  versioning {
    enabled = var.versioning_disabled
  }
}

# unknown
resource "aws_s3_bucket" "unknown_var_bucket" {
  bucket = "unknown_bucket"
  acl    = "private"

  versioning {
    enabled = var.versioning_unknown
  }
}

resource "aws_s3_bucket" "unknown_var_2_bucket" {
  bucket = "unknown_bucket"
  acl    = "private"

  versioning {
    enabled = var.versioning_disabled_2
  }
}

resource "aws_s3_bucket" "unknown_local_bucket" {
  bucket = "unknown_bucket"
  acl    = "private"

  versioning {
    enabled = local.versioning_disabled
  }
}
