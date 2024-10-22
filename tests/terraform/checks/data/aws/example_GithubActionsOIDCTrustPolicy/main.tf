# pass1

data "aws_iam_policy_document" "pass1" {
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

# pass2

data "aws_iam_policy_document" "pass2" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    action = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    principals {
      identifiers = ["arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"]
      type        = "Federated"
    }
    condition {
      test     = "StringLike"
      values   = ["repo:myOrg/myRepo:*"]
      variable = "token.actions.githubusercontent.com:sub"
    }

    condition {
      test     = "StringEquals"
      values   = ["sts.amazonaws.com"]
      variable = "token.actions.githubusercontent.com:aud"
    }
  }
}

# pass 3

data "aws_iam_policy_document" "pass3" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    action = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    principals {
      identifiers = ["arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"]
      type        = "Federated"
    }
    condition {
      test     = "StringEquals"
      values   = ["repo:myOrg/myRepo:ref:refs/heads/MyBranch"]
      variable = "token.actions.githubusercontent.com:sub"
    }

    condition {
      test     = "StringEquals"
      values   = ["sts.amazonaws.com"]
      variable = "token.actions.githubusercontent.com:aud"
    }
  }
}

data "aws_iam_policy_document" "fail1" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    action = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    principals {
      identifiers = ["arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"]
      type        = "Federated"
    }
  }
}

data "aws_iam_policy_document" "fail2" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    action = [
      "sts:AssumeRoleWithWebIdentity"
    ]
    principals {
      identifiers = ["arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"]
      type        = "Federated"
    }

    condition {
      test     = "StringEquals"
      values   = ["invalid"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}
