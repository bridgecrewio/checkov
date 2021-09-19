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
      "lambda:CreateFunction",
      "lambda:CreateEventSourceMapping",
      "dynamodb:CreateTable",
      "dynamodb:PutItem",
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

