# pass

data "aws_iam_policy_document" "pass" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "lambda:CreateFunction",
      "lambda:CreateEventSourceMapping",
      "dynamodb:CreateTable",
    ]
    resources = [
      "*",
    ]
  }
}

# fail

data "aws_iam_policy_document" "fail" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole",
      "ssm:GetParameter",
      "s3:GetObject",
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "secretsmanager:GetSecretValue",
      "s3:PutObject",
      "ec2:CreateTags"
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

