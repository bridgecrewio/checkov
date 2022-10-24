# pass

resource "aws_iam_policy_attachment" "pass" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"
}

resource "aws_iam_policy_attachment" "null" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"

  users = null
}

resource "aws_iam_policy_attachment" "empty" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"

  users = []
}

# fail

resource "aws_iam_policy_attachment" "fail" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"

  users = ["example"]
}

resource "aws_iam_user_policy" "fail" {
  user = "example"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:Describe*",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "fail" {
  user       = "example"
  policy_arn = "aws_iam_policy.policy.arn"
}
