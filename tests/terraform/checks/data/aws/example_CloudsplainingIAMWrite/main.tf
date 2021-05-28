# pass

data "aws_iam_policy_document" "restrictable" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:*",
    ]
    resources = [
      "arn:aws:s3:::bucket",
    ]
  }
}

data "aws_iam_policy_document" "unrestrictable" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "xray:PutTelemetryRecords",
      "xray:PutTraceSegments",
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
      "s3:*",
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

