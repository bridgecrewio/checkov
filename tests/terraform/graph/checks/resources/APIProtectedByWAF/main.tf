resource "aws_api_gateway_rest_api" "regional" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_rest_api" "edge" {
  name = var.name

  policy = ""

  endpoint_configuration {
    types = ["EDGE"]
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

resource "aws_api_gateway_stage" "regional" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.regional.id
  stage_name    = "example"
}

resource "aws_api_gateway_stage" "wafv2_regional" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.regional.id
  stage_name    = "example"
}

resource "aws_wafregional_web_acl_association" "regional" {
  resource_arn = aws_api_gateway_stage.regional.arn
  web_acl_id   = aws_wafregional_web_acl.foo.id
}

resource "aws_wafv2_web_acl_association" "regional" {
  resource_arn = aws_api_gateway_stage.wafv2_regional.arn
  web_acl_id   = aws_wafv2_web_acl.foo.id
}

resource "aws_api_gateway_stage" "wafv2_edge" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.edge.id
  stage_name    = "example"
}

resource "aws_wafv2_web_acl_association" "edge" {
  resource_arn = aws_api_gateway_stage.wafv2_edge.arn
  web_acl_id   = aws_wafv2_web_acl.foo.id
}