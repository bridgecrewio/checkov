
resource "aws_s3_bucket" "unknown" {
  bucket = "bucket"
}

resource "aws_s3_bucket" "fail3" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "fail2" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": ["*"]
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "fail" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": "*"
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "some_arn"
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass2" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Deny",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": "*"
        }
    ]
}
POLICY
}

resource "aws_s3_bucket_policy" "pass" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "some_arn"
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket_policy" "fail" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            }
        }
    ]
}
POLICY
}


resource "aws_s3_bucket_policy" "json" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.test.json
}

data "aws_iam_policy_document" "test" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.b.arn}/*"]
  }
}


resource "aws_s3_bucket_policy" "pass_w_condition" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnNotEquals": {
                "aws:PrincipalArn": "arn:aws:iam::12345555555555:user/username"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnNotEquals": {
                "aws:PrincipalArn": "arn:aws:iam::12345555555555:user/username"
              }
            }
        }
    ]
}
POLICY
}

# BAD:
resource "aws_s3_bucket_policy" "pass_w_condition2" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::12345555555555:user/username"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition2" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::12345555555555:user/username"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket_policy" "fail_w_condition" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::*"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "fail_w_condition" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::*"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket_policy" "fail_w_condition" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": {
                "AWS": "*"
            },
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::*"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition3" {
  bucket = "bucket"

  policy = <<POLICY
{
    "Id": "Policy1597273448050",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1597273446725",
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::bucket/*",
            "Principal": "*",
            "Condition": {
              "ArnEquals": {
                "aws:PrincipalArn": "arn:aws:iam::12345555555555:user/username"
              }
            }
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition4" {
  bucket = "bucket"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessFromSpecificVpcEndpoint",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {
        "StringEquals": {
          "aws:sourceVpce": "vpce-123abc456def7890g"
        }
      }
    }
  ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition5" {
  bucket = "bucket"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessFromSpecificVpcEndpoint",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {"ArnLike": {"aws:SourceArn": "arn:aws:cloudtrail:*:111122223333:trail/*"}}
    }
  ]
}
POLICY
}

resource "aws_s3_bucket" "pass_w_condition6" {
  bucket = aws_s3_bucket.example_bucket.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessFromSpecificVpcEndpoint",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {
          "StringLike": {
            "aws:PrincipalOrgPath": "arn:aws:organizations::*:organization/123456789012*",
            "aws:userid": "AROAEXAMPLE1234567890123456789"
          }
        }
    }
  ]
}
POLICY
}

# Handle error
resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      jsondecode(data.aws_iam_policy_document.logs-cloudtrail-policy-acl-check.json).Statement,
      jsondecode(data.aws_iam_policy_document.s3-logs-cloudtrail-policy-write.json).Statement,
      jsondecode(data.aws_iam_policy_document.s3-logs-vpc-flow-logs-policy.json).Statement,
    )
  })
}