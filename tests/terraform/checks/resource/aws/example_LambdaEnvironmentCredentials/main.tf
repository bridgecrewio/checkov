# pass

resource "aws_lambda_function" "pass" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"

  environment {
    variables = {
      AWS_DEFAULT_REGION = "us-west-2"
    }
  }
}

resource "aws_lambda_function" "no_env" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"
}

# fail

resource "aws_lambda_function" "fail" {
  function_name = "stest-env"
  role          = ""
  runtime       = "python3.8"

  environment {
    variables = {
      AWS_ACCESS_KEY_ID     = "AKIAIOSFODNN7EXAMPLE",  # checkov:skip=CKV_SECRET_2 test secret
      AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # checkov:skip=CKV_SECRET_2 test secret
      AWS_DEFAULT_REGION    = "us-west-2"
    }
  }
}
