resource "awscc_lambda_function" "pass" {
  function_name = "encrypted-lambda"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  
  environment = {
    variables = {
      ENV_VAR_1 = "value1"
      ENV_VAR_2 = "value2"
    }
  }
  
  kms_key_arn = "arn:aws:kms:us-east-1:123456789012:key/1234abcd-12ab-34cd-56ef-1234567890ab"
}

resource "awscc_lambda_function" "fail" {
  function_name = "unencrypted-lambda"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  
  environment = {
    variables = {
      ENV_VAR_1 = "value1"
      ENV_VAR_2 = "value2"
    }
  }
  
  # No KMS key specified - uses AWS default encryption
}
