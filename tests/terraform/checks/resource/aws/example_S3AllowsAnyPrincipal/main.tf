
resource "aws_s3_bucket" "fail" {
  bucket = "bucketfail"

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

resource "aws_s3_bucket_policy" "fail2" {
  bucket = "bucketfail2"

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

resource "aws_s3_bucket" "fail3" {
  bucket = "bucketfail3"

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

resource "aws_s3_bucket" "fail4" {
  bucket = "bucketfail4"

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
  bucket = "bucketpass"

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

resource "aws_s3_bucket" "pass_deny" {
  bucket = "bucketpass_deny"

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

resource "aws_s3_bucket_policy" "s3-policy" {
  bucket = "bucket-policy"

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

