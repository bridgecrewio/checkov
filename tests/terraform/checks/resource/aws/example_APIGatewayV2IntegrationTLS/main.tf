# PASS: VPC_LINK with tls_config and server_name_to_verify set
resource "aws_apigatewayv2_integration" "pass_vpc_link_tls" {
  api_id             = "api-123"
  integration_type   = "HTTP_PROXY"
  integration_uri    = "https://example.com"
  connection_type    = "VPC_LINK"
  connection_id      = "vpc-link-123"
  integration_method = "GET"

  tls_config {
    server_name_to_verify = "example.com"
  }
}

# PASS: non-VPC_LINK connection_type (auto-pass, not a private integration)
resource "aws_apigatewayv2_integration" "pass_internet" {
  api_id           = "api-123"
  integration_type = "HTTP_PROXY"
  integration_uri  = "https://example.com"
  connection_type  = "INTERNET"
}

# PASS: no connection_type specified (defaults to INTERNET, auto-pass)
resource "aws_apigatewayv2_integration" "pass_no_connection_type" {
  api_id           = "api-123"
  integration_type = "HTTP_PROXY"
  integration_uri  = "https://example.com"
}

# FAIL: VPC_LINK without tls_config block
resource "aws_apigatewayv2_integration" "fail_no_tls_config" {
  api_id             = "api-123"
  integration_type   = "HTTP_PROXY"
  integration_uri    = "https://example.com"
  connection_type    = "VPC_LINK"
  connection_id      = "vpc-link-123"
  integration_method = "GET"
}

# FAIL: VPC_LINK with tls_config but empty server_name_to_verify
resource "aws_apigatewayv2_integration" "fail_empty_server_name" {
  api_id             = "api-123"
  integration_type   = "HTTP_PROXY"
  integration_uri    = "https://example.com"
  connection_type    = "VPC_LINK"
  connection_id      = "vpc-link-123"
  integration_method = "GET"

  tls_config {
    server_name_to_verify = ""
  }
}
