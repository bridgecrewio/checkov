resource "aws_kms_key" "pass" {
    enable_key_rotation = true
}

resource "aws_kms_key" "pass2" {
  enable_key_rotation = true
  policy = jsonencode({
    Id = "example"
    Statement = [
      {
        Action = "kms:*"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }

        Resource = "*"
        Sid      = "Enable IAM User Permissions"
      },
    ]
    Version = "2012-10-17"
  })
}

resource "aws_kms_key_policy" "pike" {
  key_id = aws_kms_key.pass.id
  policy = jsonencode({
    Id = "example"
    Statement = [
      {
        Action = "kms:*"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }

        Resource = "*"
        Sid      = "Enable IAM User Permissions"
      },
    ]
    Version = "2012-10-17"
  })
}

resource "aws_kms_key" "fail" {
  enable_key_rotation = true
}


resource "aws_s3_bucket" "ignore" {}
