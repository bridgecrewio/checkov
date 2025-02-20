data "aws_iam_policy_document" "pass_aud_first" {
    statement {
      effect  = "Allow"
      actions = ["sts:AssumeRoleWithWebIdentity"]

      principals {
        type        = "Federated"
        identifiers = ["arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com"]
      }
      condition {
        test     = "StringEquals"
        values   = ["sts.pass_aud_first.com"]
        variable = "token.actions.githubusercontent.com:aud"
      }
      condition {
        test     = "StringLike"
        values   = ["repo:org/our-repo-name:*"]
        variable = "token.actions.githubusercontent.com:sub"
      }
  }
}

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

# fail for wildcard as condition
data "aws_iam_policy_document" "fail-wildcard" {
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
      values   = ["*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}
# fail for abusable value as condition
data "aws_iam_policy_document" "fail-abusable" {
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
      values   = ["workflow:github-actions:repo:myOrg/myRepo:ref:refs/heads/MyBranch"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}
# fail for condition that asserts wildcard
data "aws_iam_policy_document" "fail-wildcard-assertion" {
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
      values   = ["repo:*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}
# fail for misused "repo" condition
data "aws_iam_policy_document" "fail-misused-repo" {
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
      values   = ["repo:myOrg*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}
# pass for org only "repo" condition
data "aws_iam_policy_document" "pass-org-only" {
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
      values   = ["repo:myOrg/*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}