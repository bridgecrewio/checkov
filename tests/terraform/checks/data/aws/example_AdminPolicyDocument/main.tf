# pass

data "aws_iam_policy_document" "pass" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:Describe*",
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "list" {
  version = "2012-10-17"

  statement = [{
    actions = [
      "s3:GetObject"
    ]
    resources = [
      "${aws_s3_bucket.default.arn}/*"
    ]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }]

  # Support replication ARNs
  statement = ["${flatten(data.aws_iam_policy_document.replication.*.statement)}"]

  # Support deployment ARNs
  statement = ["${flatten(data.aws_iam_policy_document.deployment.*.statement)}"]
}

# fail

data "aws_iam_policy_document" "fail" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "*"
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "no_effect" {
  version = "2012-10-17"

  statement {
    actions = [
      "*"
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

