# Test data type with AdministratorAccess via name - Fail
data "aws_iam_policy" "administrator_access_name_fail" {
  name = "AdministratorAccess"
}
# Test data type with AdministratorAccess via ARN - Fail
data "aws_iam_policy" "administrator_access_arn_fail" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# Test data type with other policy via name - Pass
data "aws_iam_policy" "other_access_name_pass" {
  name = "AmazonEC2ReadOnlyAccess"
}
# Test data type with other policy via ARN - Pass
data "aws_iam_policy" "other_access_arn_pass" {
  arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test user policy attachment with AdministratorAccess - Fail
resource "aws_iam_user_policy_attachment" "test_attach_fail" {
  user       = aws_iam_user.user.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# Test user policy attachment with other policy - Fail
resource "aws_iam_user_policy_attachment" "test_attach_pass" {
  user       = aws_iam_user.user2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

# Test role policy attachment with AdministratorAccess - Fail
resource "aws_iam_role_policy_attachment" "test_attach_fail" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# Test group policy attachment with AdministratorAccess - Fail
resource "aws_iam_group_policy_attachment" "test_attach_fail" {
  group      = aws_iam_group.group.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# Test SSO policy attachment with AdministratorAccess - Fail
resource "aws_ssoadmin_managed_policy_attachment" "administrator_access_fail" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.admins.arn
}
# Test SSO policy attachment with other policy - Pass
resource "aws_ssoadmin_managed_policy_attachment" "amazon_ec2_read_only_access_pass" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.my_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.viewers.arn
}