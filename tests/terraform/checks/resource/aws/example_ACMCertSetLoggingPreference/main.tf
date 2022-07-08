resource "aws_acm_certificate" "pass" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }
  options {
    certificate_transparency_logging_preference = "ENABLED"
  }
  #   lifecycle {
  #     create_before_destroy = true
  #   }
}

resource "aws_acm_certificate" "pass2" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }
  #  options {
  #    certificate_transparency_logging_preference = "DISABLED"
  #  }
  #   lifecycle {
  #     create_before_destroy = true
  #   }
}

resource "aws_acm_certificate" "fail" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Environment = "test"
  }
  options {
    certificate_transparency_logging_preference = "DISABLED"
  }
  #   lifecycle {
  #     create_before_destroy = true
  #   }
}
