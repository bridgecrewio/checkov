resource "aws_acm_certificate" "pass" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate" "fail" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }

  lifecycle {
    create_before_destroy = false
  }
}

resource "aws_acm_certificate" "fail2" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }
}