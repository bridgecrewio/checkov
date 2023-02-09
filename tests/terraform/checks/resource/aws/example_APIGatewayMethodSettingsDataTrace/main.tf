resource "aws_api_gateway_method_settings" "fail" {
  rest_api_id = aws_api_gateway_rest_api.test.id
  stage_name  = aws_api_gateway_stage.test.stage_name
  method_path = "path1/GET"

  settings {
    data_trace_enabled = true
  }
}

resource "aws_api_gateway_method_settings" "pass_explicit" {
  rest_api_id = aws_api_gateway_rest_api.test.id
  stage_name  = aws_api_gateway_stage.test.stage_name
  method_path = "path1/GET"

  settings {
    data_trace_enabled = false
  }
}

resource "aws_api_gateway_method_settings" "pass_implicit" {
  rest_api_id = aws_api_gateway_rest_api.test.id
  stage_name  = aws_api_gateway_stage.test.stage_name
  method_path = "path1/GET"
}