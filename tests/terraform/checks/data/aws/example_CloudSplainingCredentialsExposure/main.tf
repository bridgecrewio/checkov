# pass

data "aws_iam_policy_document" "allowed_action" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
        "ecr:GetAuthorizationToken",
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "deny" {
  version = "2012-10-17"

  statement {
   sid       = "DenyOutsideCallers"
   effect    = "Deny"
   actions   = ["*"]
   resources = ["*"]

   condition {
     test     = "NotIpAddress"
     variable = "aws:SourceIp"
     values = [
       "1.2.3.4/16"
     ]
   }

   condition {
     test     = "Bool"
     variable = "aws:ViaAWSService"
     values   = ["false"]
   }
 }
}

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
      "s3:GetObject",
      "iam:CreateAccessKey"
    ]
    resources = [
      "*",
    ]
  }
}

# unknown

