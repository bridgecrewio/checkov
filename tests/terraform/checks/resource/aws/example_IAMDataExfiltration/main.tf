# pass

resource "aws_iam_policy" "pass" {
  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "lambda:CreateFunction",
          "lambda:CreateEventSourceMapping",
          "dynamodb:CreateTable",
        ],
        "Resource": "*"
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
        "Action": [
          "iam:PassRole",
          "ssm:GetParameter",
          "s3:GetObject",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath",
          "secretsmanager:GetSecretValue",
          "s3:PutObject",
          "ec2:CreateTags"
        ],
        "Resource": "*"
      }
    ]
  }
POLICY
}

# unknown

