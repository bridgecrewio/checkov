resource "aws_api_gateway_rest_api" "pass" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_rest_api" "private" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["PRIVATE"]
  }
}

resource "aws_api_gateway_rest_api" "no_stage" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_rest_api" "no_assoc" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_stage" "no_assoc" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.no_assoc.id
  stage_name    = "example"
}

resource "aws_api_gateway_stage" "private" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.private.id
  stage_name    = "example"
}

resource "aws_api_gateway_stage" "no_api" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.no_api.id
  stage_name    = "example"
}

resource "aws_api_gateway_stage" "pass" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.pass.id
  stage_name    = "example"
}

resource "aws_wafregional_web_acl_association" "pass" {
  resource_arn = aws_api_gateway_stage.pass.arn
  web_acl_id   = aws_wafregional_web_acl.foo.id
}
