# pass

resource "aws_lambda_function" "active" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"

  tracing_config {
    mode = "Active"
  }
}

resource "aws_lambda_function" "pass_through" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"

  tracing_config {
    mode = "PassThrough"
  }
}

# fail

resource "aws_lambda_function" "default" {
  function_name = "test-env"
  role          = ""
  runtime       = "python3.8"
}
