data "aws_iam_policy_document" "fail" {
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

data "aws_iam_policy_document" "pass2" {
  version = "2012-10-17"

  statement {
    effect = "Deny"
    actions = [
      "s3:Describe*",
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "pass" {
  statement {
    sid = "1"

    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucketLocation",
    ]

    resources = [
      "arn:aws:s3:::*",
    ]
  }

  statement {
    actions = [
      "s3:ListBucket",
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}",
    ]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "",
        "home/",
        "home/&{aws:username}/",
      ]
    }
  }

  statement {
    actions = [
      "s3:*",
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}/home/&{aws:username}",
      "arn:aws:s3:::${var.s3_bucket_name}/home/&{aws:username}/*",
    ]
  }
}

data "aws_iam_policy_document" "pass_unrestrictable" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "pass_condition" {
  statement {
    actions = [
      "kms:GenerateDataKey",
      "kms:Decrypt"
    ]
    resources = [
      "*"
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [
        "arn"
      ]
    }
  }
}
