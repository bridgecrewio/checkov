resource "aws_iam_user" "acme_user" {
  name = "acme"
}

// "ecr:GetAuthorizationToken" must be permitted to all ecr resources.
resource "aws_iam_user_policy" "u_p" {
  name = "acme_policy"
  user = aws_iam_user.acme_user.name

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:ListTaskDefinitions",
                "ecs:RegisterTaskDefinition"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}
