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

### variables not in scope or dont exist ###

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

resource "aws_s3_bucket" "unknown_enabled_bucket" {
  bucket = "unknown_bucket"
  acl    = "private"

  versioning {
    enabled = var.versioning_enabled_2
  }
}

resource "aws_s3_bucket" "unknown_enabled_local_bucket" {
  bucket = "unknown_bucket"
  acl    = "private"

  versioning {
    enabled = local.versioning_enabled
  }
}

resource "aws_s3_bucket" "unknown_data_acl_bucket" {
  bucket = "unknown_acl_bucket"
  acl    = "private"

  versioning {
    enabled = data.doesnt_exist
  }
}

resource "aws_s3_bucket" "unknown_data_acl_bucket" {
  bucket = "unknown_acl_bucket"
  acl    = "private"

  versioning {
    enabled = module.doesnt_exist
  }
}