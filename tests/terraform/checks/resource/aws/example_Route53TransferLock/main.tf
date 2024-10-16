resource "aws_route53domains_registered_domain" "pass_missing" {
  domain_name = "example.com"

  name_server {
    name = "ns-195.awsdns-24.com"
  }

  name_server {
    name = "ns-874.awsdns-45.net"
  }

  tags = {
    Environment = "test"
  }
}

resource "aws_route53domains_registered_domain" "pass_true" {
  domain_name = "example.com"
  transfer_lock = true

  name_server {
    name = "ns-195.awsdns-24.com"
  }

  name_server {
    name = "ns-874.awsdns-45.net"
  }

  tags = {
    Environment = "test"
  }
}

resource "aws_route53domains_registered_domain" "fail" {
  domain_name = "example.com"
  transfer_lock = false

  name_server {
    name = "ns-195.awsdns-24.com"
  }

  name_server {
    name = "ns-874.awsdns-45.net"
  }

  tags = {
    Environment = "test"
  }
}