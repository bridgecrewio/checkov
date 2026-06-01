# Fixtures mirror tests/terraform/checks/data/aws/example_GithubActionsOIDCTrustPolicy/main.tf
# but expressed as aws_iam_role resources with inline `assume_role_policy = jsonencode({...})`.
#
# Each resource label matches its sibling in the data-check fixture, so the two
# test suites are easy to compare side-by-side.
#
# Resource name conventions used by the unsafe-claim assertions:
#   pass*  -> CKV_AWS_393 should return PASSED
#   fail*  -> CKV_AWS_393 should return FAILED

# pass_aud_first -- sub condition appears AFTER aud condition; safe value
resource "aws_iam_role" "pass_aud_first" {
  name = "pass_aud_first"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::000000000000:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.pass_aud_first.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:org/our-repo-name:*"
          }
        }
      }
    ]
  })
}

# pass1 -- non-OIDC assume_role_policy (EC2 service trust). Exercises the
# "no GH-OIDC federated principal -> PASSED" guard. The data-check fixture
# uses a Lambda permissions policy here; that shape is not a valid
# assume_role_policy for an IAM role, so we use the closest legitimate
# analogue: a role trusting an AWS service.
resource "aws_iam_role" "pass1" {
  name = "pass1"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

# pass2 -- repo:org/repo:* (specific repo, any branch) + aud condition
resource "aws_iam_role" "pass2" {
  name = "pass2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:myOrg/myRepo:*"
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# pass3 -- fully pinned: repo:org/repo:ref:refs/heads/branch
resource "aws_iam_role" "pass3" {
  name = "pass3"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:myOrg/myRepo:ref:refs/heads/MyBranch"
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# fail1 -- federated GH OIDC principal but NO condition at all -> FAIL
resource "aws_iam_role" "fail1" {
  name = "fail1"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
      }
    ]
  })
}

# fail2 -- sub condition value is a bare claim name ("invalid") with no claim:value pair -> FAIL
resource "aws_iam_role" "fail2" {
  name = "fail2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "invalid"
          }
        }
      }
    ]
  })
}

# fail-wildcard -- sub value is the bare wildcard "*" -> FAIL
resource "aws_iam_role" "fail-wildcard" {
  name = "fail-wildcard"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "*"
          }
        }
      }
    ]
  })
}

# fail-abusable -- abusable first claim ("workflow:...") -> FAIL
resource "aws_iam_role" "fail-abusable" {
  name = "fail-abusable"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "workflow:github-actions:repo:myOrg/myRepo:ref:refs/heads/MyBranch"
          }
        }
      }
    ]
  })
}

# fail-wildcard-assertion -- "repo:*" (wildcard as the only repo scoping) -> FAIL
resource "aws_iam_role" "fail-wildcard-assertion" {
  name = "fail-wildcard-assertion"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:*"
          }
        }
      }
    ]
  })
}

# fail-misused-repo -- "repo:myOrg*" lacks the "/" required by gh_repo_regex -> FAIL
resource "aws_iam_role" "fail-misused-repo" {
  name = "fail-misused-repo"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:myOrg*"
          }
        }
      }
    ]
  })
}

# pass-org-only -- "repo:myOrg/*" (any repo in org, any branch). Considered SAFE
# by CKV_AWS_358's design (see test_GithubActionsOIDCTrustPolicy.py's
# "pass-org-only"). Mirrored here to preserve parity.
resource "aws_iam_role" "pass-org-only" {
  name = "pass-org-only"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:myOrg/*"
          }
        }
      }
    ]
  })
}

# pass-gh-org -- variable name uses the .../github-org:sub form, so the
# gh_sub_condition regex still matches and the value is fully pinned -> PASS
resource "aws_iam_role" "pass-gh-org" {
  name = "pass-gh-org"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456123456:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com/github-org:sub" = "repo:myOrg/myRepo:ref:refs/heads/MyBranch"
            "token.actions.githubusercontent.com:aud"            = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# pass-fm-customer -- XSUP-69131 regression marker. Freddie Mac's exact value
# `repo:freddiemac/*`. Asserted as PASSED here to lock in parity with
# CKV_AWS_358's existing "pass-org-only" semantics. If this fixture's verdict
# ever flips to FAILED, it means someone tightened the policy -- which is a
# deliberate global behavior change and should not happen silently.
resource "aws_iam_role" "pass-fm-customer" {
  name = "pass-fm-customer"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:freddiemac/*"
          }
        }
      }
    ]
  })
}
