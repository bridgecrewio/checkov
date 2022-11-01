# pass

resource "aws_lambda_function" "pass" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"
  code_signing_config_arn = "123123123"
}

# fail

resource "aws_lambda_function" "fail" {
  function_name = "stest-env"
  role          = ""
  runtime       = "python3.8"
}
