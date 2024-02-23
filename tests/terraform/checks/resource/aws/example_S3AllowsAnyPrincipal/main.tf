
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
