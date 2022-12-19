resource "aws_apigatewayv2_stage" "fail_v2" {
  api_id = aws_apigatewayv2_api.example.id
  name   = "example-stage"
}

resource "aws_api_gateway_stage" "fail_v1" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.example.id
  stage_name    = "example"
}

resource "aws_apigatewayv2_stage" "pass_v2" {
  api_id = aws_apigatewayv2_api.example.id
  name   = "example-stage"
  client_certificate_id = "certificateId"
}

resource "aws_api_gateway_stage" "pass_v1" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.example.id
  stage_name    = "example"
  client_certificate_id = "certificateId"
}

