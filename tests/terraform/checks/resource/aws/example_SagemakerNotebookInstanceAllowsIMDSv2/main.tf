provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "sagemaker_execution_role" {
  name = "sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "sagemaker.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "sagemaker_execution_policy" {
  role = aws_iam_role.sagemaker_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_sagemaker_notebook_instance" "my_notebook_instance_pass" {
  name           = "MyNotebookInstance"
  instance_type  = "ml.t2.medium"
  role_arn       = aws_iam_role.sagemaker_execution_role.arn

  instance_metadata_service_configuration {
    minimum_instance_metadata_service_version = "2"
  }
}

resource "aws_sagemaker_notebook_instance" "my_notebook_instance_fail_1" {
  name           = "MyNotebookInstance"
  instance_type  = "ml.t2.medium"
  role_arn       = aws_iam_role.sagemaker_execution_role.arn

  instance_metadata_service_configuration {
    minimum_instance_metadata_service_version = "1"
  }
}

resource "aws_sagemaker_notebook_instance" "my_notebook_instance_fail_2" {
  name           = "MyNotebookInstance"
  instance_type  = "ml.t2.medium"
  role_arn       = aws_iam_role.sagemaker_execution_role.arn
}