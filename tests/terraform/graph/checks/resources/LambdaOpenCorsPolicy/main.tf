provider "aws" {
  region = "us-west-2"
}

resource "aws_lambda_function" "valid_lambda_function" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "valid_lambda_function_without_url" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function_url" "valid_lambda_function_url" {
  function_name = aws_lambda_function.valid_lambda_function.function_name
  cors {
    allow_origins = ["https://example.com"]
    allow_methods = ["GET", "POST"]
  }
  authorization_type = "AWS_IAM"
}

resource "aws_lambda_function" "valid_lambda_function_no_cors_definition" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function_url" "valid_lambda_function_url_no_cors_definition" {
  function_name = aws_lambda_function.valid_lambda_function_no_cors_definition.function_name
  authorization_type = "AWS_IAM"
}

resource "aws_lambda_function" "valid_lambda_function_only_allow_origins_star" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function_url" "valid_lambda_function_url_only_allow_origins_star" {
  function_name = aws_lambda_function.valid_lambda_function_only_allow_origins_star.function_name
  cors {
    allow_origins = ["*"]
  }
  authorization_type = "AWS_IAM"
}

resource "aws_lambda_function" "valid_lambda_function_only_allow_methods_star" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function_url" "valid_lambda_function_url_only_allow_methods_star" {
  function_name = aws_lambda_function.valid_lambda_function_only_allow_methods_star.function_name
  cors {
    allow_methods = ["*"]
  }
  authorization_type = "AWS_IAM"
}

resource "aws_lambda_function" "invalid_lambda_function" {
  function_name = "example_lambda_function"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = aws_iam_role.example_role.arn
  filename      = "lambda_function_payload.zip"
}

resource "aws_lambda_function_url" "invalid_lambda_function_url" {
  function_name = aws_lambda_function.invalid_lambda_function.function_name
  cors {
    allow_origins = ["*"]
    allow_methods = ["*"]
  }
  authorization_type = "AWS_IAM"
}

resource "aws_iam_role" "example_role" {
  name = "example_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}
