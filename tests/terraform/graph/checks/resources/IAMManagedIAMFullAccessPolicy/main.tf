# Test data type with IAMFullAccess via name - Fail
data "aws_iam_policy" "name_fail1" {
  name = "IAMFullAccess"
}
# Test data type with other policy via name - Pass
data "aws_iam_policy" "name_pass1" {
  name = "AmazonEC2ReadOnlyAccess"
}

# Test data type with IAMFullAccess via ARN - Fail
data "aws_iam_policy" "arn_fail2" {
  arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}
# Test data type with other policy via ARN - Pass
data "aws_iam_policy" "arn_pass2" {
  arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test iam role with IAMFullAccess - Fail
resource "aws_iam_role" "fail3" {
  name                = "role"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/IAMFullAccess"]
}
# Test iam role with multiple policies including IAMFullAccess - Fail
resource "aws_iam_role" "fail3a" {
  name                = "role"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess","arn:aws:iam::aws:policy/IAMFullAccess"]
}
# Test iam role with other policy - Pass
resource "aws_iam_role" "pass3" {
  name                = "role"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
}
# Test iam role with no managed policies - Pass
resource "aws_iam_role" "pass3a" {
  name                = "role"
  assume_role_policy  = data.aws_iam_policy_document.instance_assume_role_policy.json
}

# Test policy attachment with IAMFullAccess - Fail
resource "aws_iam_policy_attachment" "fail4" {
  name       = "policy"
  roles      = [aws_iam_role.fail1.name]
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}
# Test policy attachment with other policy - Pass
resource "aws_iam_policy_attachment" "pass4" {
  name       = "policy"
  role       = aws_iam_role.pass1.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# Test user policy attachment with IAMFullAccess - Fail
resource "aws_iam_user_policy_attachment" "fail5" {
  user       = aws_iam_user.user.name
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}
# Test user policy attachment with other policy - Pass
resource "aws_iam_user_policy_attachment" "pass5" {
  user       = aws_iam_user.user2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test role policy attachment with IAMFullAccess - Fail
resource "aws_iam_role_policy_attachment" "fail6" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}
# Test role policy attachment with other policy - Pass
resource "aws_iam_role_policy_attachment" "pass6" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test group policy attachment with IAMFullAccess - Fail
resource "aws_iam_group_policy_attachment" "fail7" {
  group      = aws_iam_group.group.name
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}
# Test group policy attachment with other policy - Pass
resource "aws_iam_group_policy_attachment" "pass7" {
  group      = aws_iam_group.group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test SSO policy attachment with IAMFullAccess - Fail
resource "aws_ssoadmin_managed_policy_attachment" "fail8" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
  permission_set_arn = aws_ssoadmin_permission_set.admins.arn
}
# Test SSO policy attachment with other policy - Pass
resource "aws_ssoadmin_managed_policy_attachment" "pass8" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.viewers.arn
}