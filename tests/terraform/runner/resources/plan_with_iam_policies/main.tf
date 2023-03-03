# HCL file added for easier way to re-create the plan file

provider "aws" {
  region  = "us-west-2"
  profile = "dev2"
}

resource "aws_iam_policy" "policy_pass" {
  name        = "policy_pass"
  path        = "/"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Action": "s3:*",
        "Effect": "Allow",
        "Resource": "*"
        }
    ]
  })
}

resource "aws_iam_role" "example" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"

      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "fail_1" {
  name   = "example"
  role   = aws_iam_role.example.id
  policy = data.aws_iam_policy_document.fail_1.json
}

data "aws_iam_policy_document" "fail_1" {
  statement {
    effect = "Allow"
    actions = [
      "iam:*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_group" "fail_2" {
  name = "example"
}

resource "aws_iam_group_policy" "fail_2" {
  name  = "example"
  group = aws_iam_group.fail_2.name

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:Get*",
        "iam:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
POLICY
}

resource "aws_iam_user" "fail_3" {
  name = "example"
}

resource "aws_iam_user_policy" "fail_3" {
  name   = "example"
  user   = aws_iam_user.fail_3.name
  policy = data.aws_iam_policy_document.fail_1.json
}

# couldn't create without a SSO instance
#
#data "aws_ssoadmin_instances" "example" {}
#
#resource "aws_ssoadmin_permission_set" "example" {
#  name         = "example"
#  instance_arn = tolist(data.aws_ssoadmin_instances.example.arns)[0]
#}
#
#resource "aws_ssoadmin_permission_set_inline_policy" "fail_4" {
#  instance_arn       = aws_ssoadmin_permission_set.example.instance_arn
#  permission_set_arn = aws_ssoadmin_permission_set.example.arn
#  inline_policy      = data.aws_iam_policy_document.fail_1.json
#}
