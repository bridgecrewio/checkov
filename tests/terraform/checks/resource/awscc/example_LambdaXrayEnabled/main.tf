resource "awscc_lambda_function" "pass" {
  function_name = "lambda-with-xray"
  runtime       = "python3.9"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  
  tracing_config = {
    mode = "Active"
  }
}

resource "awscc_lambda_function" "fail" {
  function_name = "lambda-without-xray"
  runtime       = "python3.9"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  
  # No tracing_config defined
}

resource "awscc_lambda_function" "fail2" {
  function_name = "lambda-with-xray-disabled"
  runtime       = "python3.9"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  
  tracing_config = {
    mode = "PassThrough"
  }
}
