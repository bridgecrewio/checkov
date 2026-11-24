resource "aws_iam_group_membership" "ok_group" {
  name = "tf-testing-group-membership"

  users = [
    aws_iam_user.user_one.name,
    aws_iam_user.user_two.name,
  ]

  group = aws_iam_group.group.name
}

resource "aws_iam_group" "group" {
  name = "test-group"
}

resource "aws_iam_user" "user_one" {
  name = "test-user"
}

resource "aws_iam_user" "user_two" {
  name = "test-user-two"
}


resource "aws_iam_group_membership" "bad_group" {
  name = "tf-testing-group-membership"


  group = aws_iam_group.bad_group.name
}


resource "aws_iam_group" "bad_group" {
  name = "test-group"
}

resource "aws_iam_group" "lonely_group" {
  name = "lonely-group"
}

resource "aws_iam_group" "alt_group" {
  name = "alt-group"
}

resource "aws_iam_user_group_membership" "alt_membership" {
  user = aws_iam_user.user_one.name
  groups = [
    aws_iam_group.alt_group.name,
  ]
}