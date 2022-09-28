# pass

resource "aws_iam_policy_attachment" "pass" {
  name       = "example"
  roles      = [aws_iam_role.role.name]
  policy_arn = "aws_iam_policy.policy.arn"
}

resource "aws_iam_policy_attachment" "null" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"
  roles      = [aws_iam_role.role.name]
  users = null
}

resource "aws_iam_policy_attachment" "empty" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"
  roles      = [aws_iam_role.role.name]
  users = []
}

# fail
resource "aws_iam_user" "bad" {
  name = "example"
  path = "/system/"

  tags = {
    tag-key = "tag-value"
  }
}

resource "aws_iam_policy_attachment" "fail" {
  name       = "example"
  policy_arn = "aws_iam_policy.policy.arn"
  roles      = [aws_iam_role.role.name]
  users = ["example"]
}


