resource "aws_sagemaker_notebook_instance" "pass" {
  name                    = "my-notebook-instance"
  role_arn                = aws_iam_role.role.arn
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.example.code_repository_name
  kms_key_id = aws_kms_key.test.arn

  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_notebook_instance" "fail" {
  name                    = "my-notebook-instance"
  role_arn                = aws_iam_role.role.arn
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.example.code_repository_name

  tags = {
    Name = "foo"
  }
}