# pass
resource "aws_acm_certificate" "example_pass" {
  domain_name       = "www.example.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  domain_validation_options {
    domain_name           = "www.example.com"
    validation_domain     = "example.com"
  }
}

resource "aws_acm_certificate" "example_pass2" {
  domain_name       = "example.com"
  validation_method = "DNS"

  subject_alternative_names = [
    "www.example.com",
    "blog.example.com",
    "shop.example.com"
  ]

  lifecycle {
    create_before_destroy = true
  }
}



# fail
resource "aws_acm_certificate" "example_fail" {
  domain_name       = "*.example.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  domain_validation_options {
    domain_name           = "*.example.com"
    validation_domain     = "example.com"
  }
}

# fail: using subject_alternative_names
resource "aws_acm_certificate" "example_fail_bad_subject" {
  domain_name       = "example.com"  # Primary domain without wildcard
  validation_method = "DNS"

  subject_alternative_names = [
    "*.sub.example.com",  # Wildcard in the subject alternative names
    "www.example.com",
    "api.example.com"
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# fail: using subject_alternative_names
resource "aws_acm_certificate" "example_fail_bad_domain" {
  domain_name       = "*example.com"  # Primary domain wit wildcard
  validation_method = "DNS"

  subject_alternative_names = [
    "sub.example.com",
    "www.example.com",
    "api.example.com"
  ]

  lifecycle {
    create_before_destroy = true
  }
}
