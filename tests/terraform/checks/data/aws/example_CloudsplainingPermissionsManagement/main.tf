# pass

data "aws_iam_policy_document" "pass" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      "arn:aws:s3:::example",
    ]
  }
}

# fail

data "aws_iam_policy_document" "fail" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "iam:*"
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

