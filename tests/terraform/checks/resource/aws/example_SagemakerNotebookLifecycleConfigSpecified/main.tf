resource "aws_sagemaker_notebook_instance" "lifecycle_config_fail" {
  name          = "my-notebook-instance"
  role_arn      = aws_iam_role.role.arn
  instance_type = "ml.t2.medium"

  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_notebook_instance" "lifecycle_config_pass" {
  name          = "my-notebook-instance"
  role_arn      = aws_iam_role.role.arn
  instance_type = "ml.t2.medium"
  lifecycle_config_name = "test_lifecycle"

  tags = {
    Name = "foo"
  }
}