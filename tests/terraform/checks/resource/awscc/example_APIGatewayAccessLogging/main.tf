resource "awscc_apigateway_stage" "pass" {
  rest_api_id = "api-12345"
  stage_name  = "prod"
  
  access_log_setting = {
    destination_arn = "arn:aws:logs:us-east-1:123456789012:log-group:api-gateway-logs"
    format          = "$context.identity.sourceIp $context.identity.caller $context.identity.user [$context.requestTime] \"$context.httpMethod $context.resourcePath $context.protocol\" $context.status $context.responseLength $context.requestId"
  }
}

resource "awscc_apigateway_stage" "fail" {
  rest_api_id = "api-12345"
  stage_name  = "dev"
  # No access_log_setting defined
}
