resource "aws_apigatewayv2_route" "fail" {
  api_id    = aws_apigatewayv2_api.example.id
  route_key = "$default"
}

resource "aws_apigatewayv2_route" "fail2" {
  api_id    = aws_apigatewayv2_api.example.id
  route_key = "$default"
  authorization_type = "NONE"
}

resource "aws_apigatewayv2_route" "pass2" {
  api_id    = aws_apigatewayv2_api.example.id
  route_key = "$default"
  authorization_type = "JWT"
}

resource "aws_apigatewayv2_route" "pass" {
  api_id    = aws_apigatewayv2_api.example.id
  route_key = "$default"
  authorization_type = "AWS_IAM"
}