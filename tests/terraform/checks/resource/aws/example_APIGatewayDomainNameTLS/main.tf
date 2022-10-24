provider "aws" {
  region = "eu-west-2"
}

resource "aws_api_gateway_domain_name" "fail" {
  security_policy = "TLS_1_0"
  domain_name     = "api.freebeer10.com"
}

resource "aws_api_gateway_domain_name" "pass" {
  security_policy = "TLS_1_2"
  domain_name     = "api.freebeer12.com"
}
