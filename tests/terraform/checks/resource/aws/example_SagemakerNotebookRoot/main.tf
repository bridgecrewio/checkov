resource "aws_sagemaker_notebook_instance" "fail" {
  name                    = "my-notebook-instance"
  role_arn                = aws_iam_role.role.arn
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.example.code_repository_name
  root_access = "Enabled"
  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_notebook_instance" "fail2" {
  name                    = "my-notebook-instance"
  role_arn                = aws_iam_role.role.arn
  instance_type           = "ml.t2.medium"
  default_code_repository = aws_sagemaker_code_repository.example.code_repository_name
  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_notebook_instance" "pass" {
  name                    = "my-notebook-instance"
  role_arn                = aws_iam_role.role.arn
  instance_type           = "ml.t2.medium"
  subnet_id = aws_subnet.pike.id
  default_code_repository = aws_sagemaker_code_repository.example.code_repository_name
  root_access = "Disabled"
  tags = {
    Name = "foo"
  }
}