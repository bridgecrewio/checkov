# Fail

data "aws_iam_policy" "fail1" {
  name = "AdministratorAccess"
}

data "aws_iam_policy" "fail2" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# Pass

data "aws_iam_policy" "pass1" {
  name = "AmazonS3ReadOnlyAccess"
}

data "aws_iam_policy" "pass2" {
  arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}