# Pass: not public
resource "aws_s3_bucket_acl" "pass_private" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_private,
    aws_s3_bucket_public_access_block.pass_private,
  ]

  bucket = aws_s3_bucket.pass_private.id
  acl    = "private"
}

# Pass: public but restricted
resource "aws_s3_bucket_public_access_block" "pass_restricted" {
  bucket = aws_s3_bucket.pass_restricted.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = true
}

resource "aws_s3_bucket_acl" "pass_restricted" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_restricted,
    aws_s3_bucket_public_access_block.pass_restricted,
  ]

  bucket = aws_s3_bucket.pass_restricted.id
  acl    = "public-read"
}

# Pass: public grant, but blocked
resource "aws_s3_bucket_acl" "pass_grant_blocked" {
  depends_on = [aws_s3_bucket_ownership_controls.pass_grant_blocked]

  bucket = aws_s3_bucket.pass_grant_blocked.id
  access_control_policy {
    grant {
      grantee {
        id   = data.aws_canonical_user_id.pass_grant_blocked.id
        type = "CanonicalUser"
      }
      permission = "READ"
    }

    grant {
      grantee {
        type = "Group"
        uri  = "http://acs.amazonaws.com/groups/global/AllUsers"
      }
      permission = "READ_ACP"
    }

    owner {
      id = data.aws_canonical_user_id.pass_grant_blocked.id
    }
  }
}

resource "aws_s3_bucket_public_access_block" "pass_grant_blocked" {
  bucket = aws_s3_bucket.pass_grant_blocked.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Pass: website bucket
resource "aws_s3_bucket_public_access_block" "pass_website" {
  bucket = aws_s3_bucket.pass_website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "pass_website" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_website,
    aws_s3_bucket_public_access_block.pass_website,
  ]

  bucket = aws_s3_bucket.pass_website.id
  acl    = "public-read"
}

resource "aws_s3_bucket_website_configuration" "pass_website" {
  bucket = aws_s3_bucket.pass_website.id
}

# Fail: data policy
resource "aws_s3_bucket_public_access_block" "fail1" {
  bucket = aws_s3_bucket.fail1.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "fail1" {
  depends_on = [
    aws_s3_bucket_ownership_controls.fail1,
    aws_s3_bucket_public_access_block.fail1,
  ]

  bucket = aws_s3_bucket.fail1.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "fail1" {
  bucket = aws_s3_bucket.fail1.id
  policy = data.aws_iam_policy_document.fail1.json
}

data "aws_iam_policy_document" "fail1" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["123456789012"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.fail1.arn,
    ]
  }
}

# Pass: data policy
resource "aws_s3_bucket_public_access_block" "pass_policy1" {
  bucket = aws_s3_bucket.pass_policy1.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "pass_policy1" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_policy1,
    aws_s3_bucket_public_access_block.pass_policy1,
  ]

  bucket = aws_s3_bucket.pass_policy1.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "pass_policy1" {
  bucket = aws_s3_bucket.pass_policy1.id
  policy = data.aws_iam_policy_document.pass_policy1.json
}

data "aws_iam_policy_document" "pass_policy1" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["123456789012"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.pass_policy1.arn,
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"

      values = [
        "true",
      ]
    }
  }
}

# Pass: inline policy
resource "aws_s3_bucket_public_access_block" "pass_policy2" {
  bucket = aws_s3_bucket.pass_policy2.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "pass_policy2" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_policy2,
    aws_s3_bucket_public_access_block.pass_policy2,
  ]

  bucket = aws_s3_bucket.pass_policy2.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "pass_policy2" {
  bucket = aws_s3_bucket.pass_policy2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "MYBUCKETPOLICY"
    Statement = [
      {
        Sid       = "IPAllow"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.pass_policy2.arn
        ]
        Condition = {
          IpAddress = {
            "aws:SourceIp" = "8.8.8.8/32"
          }
        }
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.pass_policy2.arn
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}

# Pass: inline policy
resource "aws_s3_bucket_public_access_block" "pass_policy3" {
  bucket = aws_s3_bucket.pass_policy3.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "pass_policy3" {
  depends_on = [
    aws_s3_bucket_ownership_controls.pass_policy3,
    aws_s3_bucket_public_access_block.pass_policy3,
  ]

  bucket = aws_s3_bucket.pass_policy3.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "pass_policy2" {
  bucket = aws_s3_bucket.pass_policy3.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "MYBUCKETPOLICY"
    Statement = [
      {
        Sid       = "IPAllow"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.pass_policy3.arn
        ]
        Condition = {
          IpAddress = {
            "aws:SourceIp" = "8.8.8.8/32"
          }
        }
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.pass_policy3.arn
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "true"
          }
        }
      }
    ]
  })
}

# Fail: inline policy
resource "aws_s3_bucket_public_access_block" "fail2" {
  bucket = aws_s3_bucket.fail2.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_acl" "fail2" {
  depends_on = [
    aws_s3_bucket_ownership_controls.fail2,
    aws_s3_bucket_public_access_block.fail2,
  ]

  bucket = aws_s3_bucket.fail2.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "fail2" {
  bucket = aws_s3_bucket.fail2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "MYBUCKETPOLICY"
    Statement = [
      {
        Sid       = "IPAllow"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.fail2.arn
        ]
        Condition = {
          IpAddress = {
            "aws:SourceIp" = "8.8.8.8/32"
          }
        }
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.fail2.arn
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}