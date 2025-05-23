resource "awscc_apigateway_stage" "pass" {
  rest_api_id = "api-id"
  stage_name  = "example"
  tracing_enabled = true
}

resource "awscc_apigateway_stage" "fail" {
  rest_api_id = "api-id"
  stage_name  = "example"
  tracing_enabled = false
}

resource "awscc_apigateway_stage" "fail2" {
  rest_api_id = "api-id"
  stage_name  = "example"
  # tracing_enabled not set defaults to false
}
