# pass

resource "aws_lambda_function" "pass" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.9"
  code_signing_config_arn = "123123123"
}

# fail

resource "aws_lambda_function" "fail" {
  function_name = "stest-env"
  role          = ""
  runtime       = "python3.9"
}

# pass (Image package type - code signing not applicable)

resource "aws_lambda_function" "image_pass" {
  function_name = "test-image"
  role          = ""
  package_type  = "Image"
  image_uri     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/myimage:latest"
}
