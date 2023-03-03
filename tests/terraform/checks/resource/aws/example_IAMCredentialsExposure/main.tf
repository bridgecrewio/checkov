# pass

resource "aws_iam_policy" "allowed_action" {
  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ecr:GetAuthorizationToken"
        ],
        "Resource": "*"
      }
    ]
  }
POLICY
}

resource "aws_iam_policy" "deny" {
    policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Deny",
        "Action": ["*"],
        "Resource": "*",
        "Sid": "DenyOutsideCallers",
        "Condition" : {
          "NotIpAddress": {"aws:SourceIp": "1.2.3.4/16"},
          "Bool": {"aws:ViaAWSService": "false"}
        }
      }
    ]
  }
POLICY
}

resource "aws_iam_policy" "pass" {
  policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
          "lambda:CreateFunction",
          "lambda:CreateEventSourceMapping",
          "dynamodb:CreateTable",
        ],
        "Resource": "*"
      }
      ]
    }
POLICY
}

# fail

resource "aws_iam_policy" "fail" {
    policy = <<POLICY
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "iam:CreateAccessKey"
        ],
        "Resource": "*"
      }
      ]
    }
POLICY
}

# unknown

