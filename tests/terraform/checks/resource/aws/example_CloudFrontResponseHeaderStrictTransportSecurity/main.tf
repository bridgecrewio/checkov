# pass

resource "aws_cloudfront_response_headers_policy" "pass" {
  name    = "test"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = true
      preload                    = true
    }
  }
}

# fail

resource "aws_cloudfront_response_headers_policy" "no_security_headers_config" {
  name    = "test"
}

resource "aws_cloudfront_response_headers_policy" "no_strict_transport_security" {
  name    = "test"

  security_headers_config {
    content_type_options {
      override = true
    }
  }
}

resource "aws_cloudfront_response_headers_policy" "incorrect_strict_transport_security" {
  name    = "test"

  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 1
      include_subdomains         = true
      override                   = true
      preload                    = true
    }
  }
}
