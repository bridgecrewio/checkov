# Fail

resource "aws_iam_role" "fail1" {
  name                = "fail1"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}

resource "aws_iam_policy_attachment" "fail2" {
  name       = "fail2"
  roles      = [aws_iam_role.fail1.name]
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "fail3" {
  role       = aws_iam_role.fail1.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_user_policy_attachment" "fail4" {
  user       = "user"
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_group_policy_attachment" "fail5" {
  group      = "group"
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# Test SSO policy attachment with AdministratorAccess - Fail
resource "aws_ssoadmin_managed_policy_attachment" "fail6" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.admins.arn
}

# Pass

resource "aws_iam_role" "pass1" {
  name                = "pass1"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
}

resource "aws_iam_policy_attachment" "pass2" {
  name       = "pass2"
  role       = aws_iam_role.pass1.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "pass3" {
  role       = aws_iam_role.pass1.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_user_policy_attachment" "pass4" {
  user       = "user"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_group_policy_attachment" "pass5" {
  group      = "group"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "pass6" {
  role       = aws_iam_role.fail1.name
#  policy_arn = ""  # not valid, just to simulate a TF plan behaviour
}
# Test SSO policy attachment with other policy - Pass
resource "aws_ssoadmin_managed_policy_attachment" "pass7" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.viewers.arn
}

# Data

data "aws_iam_policy_document" "instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}
