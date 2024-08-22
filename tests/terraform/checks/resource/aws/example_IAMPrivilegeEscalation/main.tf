resource "aws_iam_policy" "privilege_escalation" {
  name = "privilege_escalation"
  user = aws_iam_user.privilege_escalation_user.name

  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "iam:updateloginprofile"
        ],
        "Resource": "*"
      }
    ]
  }
POLICY
}

resource "aws_iam_policy" "passing" {
  name = "privilege_escalation"
  user = aws_iam_user.privilege_escalation_user.name

  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "lambda:CreateFunction"
        ],
        "Resource": "s3"
      }
    ]
  }
POLICY
}
