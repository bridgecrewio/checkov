# pass

resource "aws_cloudfront_distribution" "pass" {
  enabled = true

  default_cache_behavior {
    response_headers_policy_id = aws_cloudfront_response_headers_policy.pass.id
  }
}

resource "aws_cloudfront_response_headers_policy" "pass" {
  name    = "test"

  security_headers_config {
    content_security_policy {
      content_security_policy = "default-src 'none'; img-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'"
      override = true
    }
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override = true
    }
    referrer_policy {
      referrer_policy = "same-origin"
      override = true
    }
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      override                   = true
      preload                    = true
    }
    xss_protection {
      mode_block = true
      override   = true
      protection = true
    }
  }
}

# fail

resource "aws_cloudfront_distribution" "no_response_headers_policy" {
  enabled = true
}

data "aws_cloudfront_response_headers_policy" "simple_cors" {
  name = "SimpleCORS"
}

resource "aws_cloudfront_distribution" "pass2" {
  default_cache_behavior {
    response_headers_policy_id = data.aws_cloudfront_response_headers_policy.simple_cors.id
    allowed_methods            = []
    cached_methods             = []
    target_origin_id           = ""
    viewer_protocol_policy     = ""
  }
  enabled = false
  origin {
    domain_name = ""
    origin_id   = ""
  }
  restrictions {
    geo_restriction {
      restriction_type = ""
    }
  }
  viewer_certificate {}
}
