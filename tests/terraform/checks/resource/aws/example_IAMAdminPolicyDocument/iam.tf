resource "aws_iam_policy" "pass1" {
  name = "pass1"
  path = "/"
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:ListBucket*",
        "s3:HeadBucket",
        "s3:Get*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "arn:aws:s3:::b2",
        "arn:aws:s3:::b2/*"
      ],
      "Sid": ""
    },
    {
      "Action": "s3:PutObject*",
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::b1/*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_iam_policy" "fail1" {
  name = "fail1"
  path = "/"
  # the policy doesn't actually make sense, but it tests checking arrays for *
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:HeadBucket",
        "*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "*"
      ],
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_iam_policy" "fail2" {
  name = "fail2"
  path = "/"
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "*"
      ],
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_iam_policy" "fail3" {
  name = "fail3"
  path = "/"
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": "*",
      "Effect": "Allow",
      "Resource": "*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_iam_policy" "fail4" {
  name = "fail4"
  path = "/"
  # implicit allow, not actually valid, but it's a default that we check
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": "*",
      "Resource": "*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_iam_policy" "pass2" {
  name = "pass2"
  path = "/"
  # deny
  policy = <<POLICY
{
  "Statement": [
    {
      "Action": "*",
      "Effect": "Deny",
      "Resource": "*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}


resource "aws_ssoadmin_permission_set_inline_policy" "pass1" {
  instance_arn       = aws_ssoadmin_permission_set.example.instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.example.arn
  inline_policy = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:ListBucket*",
        "s3:HeadBucket",
        "s3:Get*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "arn:aws:s3:::b2",
        "arn:aws:s3:::b2/*"
      ],
      "Sid": ""
    },
    {
      "Action": "s3:PutObject*",
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::b1/*",
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}

resource "aws_ssoadmin_permission_set_inline_policy" "fail1" {
  instance_arn       = aws_ssoadmin_permission_set.example.instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.example.arn
  inline_policy = <<POLICY
{
  "Statement": [
    {
      "Action": [
        "s3:HeadBucket",
        "*"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::b1",
        "arn:aws:s3:::b1/*",
        "*"
      ],
      "Sid": ""
    }
  ],
  "Version": "2012-10-17"
}
POLICY
}