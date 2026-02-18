resource "awscc_lambda_function" "pass" {
  function_name = "lambda-with-dlq"
  runtime       = "python3.9"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  
  dead_letter_config = {
    target_arn = "arn:aws:sqs:us-west-2:123456789012:dlq-queue"
  }
}

resource "awscc_lambda_function" "fail" {
  function_name = "lambda-without-dlq"
  runtime       = "python3.9"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  
  # No dead_letter_config defined
}
