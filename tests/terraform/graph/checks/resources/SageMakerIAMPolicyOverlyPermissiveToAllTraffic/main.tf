resource "aws_iam_role" "example_role" {
  name = "example_role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"
        Resource = "*"
      }
    ]
  })
  assume_role_policy = ""
}

resource "aws_sagemaker_notebook_instance" "fail1" {
  name   = "example-notebook-instance"
  role_arn = aws_iam_role.example_role.arn
  instance_type = ""
}

resource "aws_iam_role" "example_role_restricted" {
  name = "example_role_restricted"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:ListBucket"
        Resource = "arn:aws:s3:::example-bucket"
      }
    ]
  })
  assume_role_policy = ""
}

resource "aws_sagemaker_notebook_instance" "pass1" {
  name   = "example-notebook-instance-restricted"
  role_arn = aws_iam_role.example_role_restricted.arn
  instance_type = ""
}

resource "aws_iam_role" "example_role_no_policy" {
  name = "example_role_no_policy"
  assume_role_policy = ""
}

resource "aws_sagemaker_notebook_instance" "pass2" {
  name   = "example-notebook-instance-no-policy"
  role_arn = aws_iam_role.example_role_no_policy.arn
  instance_type = ""
}
