# pass

resource "aws_s3_bucket" "private_acl" {
  bucket = "example"

  acl = "private"
}

resource "aws_s3_bucket" "no_acl" {
  bucket = "example_no_acl"
}

resource "aws_s3_bucket" "unknown_var" {
  bucket = "example"

  acl = var.unknown_var
}

variable "unknown_var" {
  description = "unknown value"
}

resource "aws_s3_bucket" "unknown_var_legacy" {
  bucket = "example"

  acl = "${var.whatever}"
}

# fail

resource "aws_s3_bucket" "public_read_write" {
  bucket = "example"
  acl    = "public-read-write"
}

# provider version 4

# pass
resource "aws_s3_bucket" "private_acl_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "private_acl_v4" {
  bucket = aws_s3_bucket.private_acl_v4.id
  acl    = "private"
}

resource "aws_s3_bucket" "unknown_var_v4_legacy" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "unknown_var_v4_legacy" {
  bucket = aws_s3_bucket.unknown_var_v4_legacy.id
  acl    = "${local.whatever}"
}

resource "aws_s3_bucket" "no_grant" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "no_grant" {
  bucket = aws_s3_bucket.no_grant.bucket

  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.this.id
    }
  }
}

resource "aws_s3_bucket" "grant_onwer" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "grant_onwer" {
  bucket = aws_s3_bucket.grant_onwer.bucket

  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.current.id
    }
    grant {
      grantee {
        id   = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
      permission = "READ"
    }
  }
}

# fail

resource "aws_s3_bucket" "public_read_write_v4" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "public_read_write_v4" {
  bucket = aws_s3_bucket.public_read_write_v4.id
  acl    = "public-read-write"
}

resource "aws_s3_bucket" "grant_public_write_all" {
  bucket = "example"
}

resource "aws_s3_bucket_acl" "grant_public_write_all" {
  bucket = aws_s3_bucket.grant_public_write_all.bucket

  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.current.id
    }
    grant {
      grantee {
        id   = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
      permission = "READ"
    }
    grant {
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AllUsers"
      }
      permission = "WRITE"
    }
  }
}

# pass
resource "aws_s3_bucket" "bucket_with_read_acl" {
  bucket = "abc"
}

resource "aws_s3_bucket_acl" "acl_for_bucket_with_read_acl" {
  bucket = aws_s3_bucket.bucket_with_read_acl.id
  access_control_policy {
    grant {
      grantee {
        uri   = "http://acs.amazonaws.com/groups/global/AllUsers"
        type = "Group"
      }
      permission = "READ"
    }
  }
}