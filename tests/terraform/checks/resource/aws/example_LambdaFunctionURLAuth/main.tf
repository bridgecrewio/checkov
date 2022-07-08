resource "aws_lambda_function_url" "fail" {
  function_name      = aws_lambda_function.test.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_function_url" "pass" {
  function_name      = aws_lambda_function.test.function_name
  qualifier          = "my_alias"
  authorization_type = "AWS_IAM"
}