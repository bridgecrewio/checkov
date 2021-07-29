resource "aws_iam_group_membership" "ok_group" {
  name = "tf-testing-group-membership"

  users = [
    aws_iam_user.user_good.name,
  ]

  group = aws_iam_group.group.name
}

resource "aws_iam_group" "group" {
  name = "test-group"
}

resource "aws_iam_user" "user_good" {
  name = "test-user"
}

resource "aws_iam_user" "user_bad" {
  name = "test-user-two"
}


resource "aws_iam_group_membership" "bad_group" {
  name = "tf-testing-group-membership"
  users = []
  group = aws_iam_group.bad_group.name
}

resource "aws_iam_group" "bad_group" {
  name = "test-group"
}