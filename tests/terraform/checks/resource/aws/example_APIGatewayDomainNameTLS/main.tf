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

resource "aws_api_gateway_domain_name" "pass2" {
  security_policy = "SecurityPolicy_TLS13_1_3_2025_09"
  domain_name     = "api.modern-tls13.com"
}

resource "aws_api_gateway_domain_name" "pass3" {
  security_policy = "SecurityPolicy_TLS13_1_2_2021_06"
  domain_name     = "api.tls13-12.com"
}
