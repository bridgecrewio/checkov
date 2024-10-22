# pass

resource "aws_iam_policy" "pass" {
  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["s3:*"],
        "Resource": "arn:aws:s3:::example"
      }
    ]
  }
POLICY
}

# fail

resource "aws_iam_policy" "fail" {
  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["iam:*"],
        "Resource": "*"
      }
    ]
  }
POLICY
}

# unknown

