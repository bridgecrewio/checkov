# pass

resource "aws_iam_user" "pass" {
  name = "tech-user"
}

# fail

resource "aws_iam_user" "fail" {
  name = "human-user"
}

resource "aws_iam_user_login_profile" "fail" {
  user    = aws_iam_user.fail.name
  pgp_key = "keybase:human-user"
}
