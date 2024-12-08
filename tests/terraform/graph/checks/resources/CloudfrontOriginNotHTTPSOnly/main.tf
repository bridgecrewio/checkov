# pass: enabled=false (required)
resource "aws_cloudfront_distribution" "example_pass_disabled" {
  enabled = false # disabled

  origin {
    domain_name = "example.data.mediastore.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "match-viewer"  # Does not enforce HTTPS only, matches RQL condition to fail
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}


# pass: enabled=true; origin->custom_origin_config not exists (origin is required)
resource "aws_cloudfront_distribution" "example_pass_nocustomorigin" {
  enabled = true # enabled

  origin {
    domain_name = "example.data.mediastore.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    # no custom origin
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}


# pass: enabled=true; origin->custom_origin_config->origin_protocol_policy=https-only
resource "aws_cloudfront_distribution" "example_pass_httpsonly" {
  enabled = true # enabled

  origin {
    domain_name = "example.data.mediastore.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "https-only"  # HTTPS only
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# pass: enabled=true; origin->custom_origin_config->origin_protocol_policy=match-viewer; origin->domain_name not contains (".data.mediastore." or domainName contains ".mediapackage." or domainName contains ".elb.")
resource "aws_cloudfront_distribution" "example_pass_domain" {
  enabled = true # enabled

  origin {
    domain_name = "example.com" # safe domain
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "match-viewer"  # Does not enforce HTTPS only, matches RQL condition to fail
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}


# fail: enabled=true; origin->custom_origin_config->origin_protocol_policy=match-viewer; origin->domain_name contains "mediastore"
resource "aws_cloudfront_distribution" "example_fail" {
  enabled = true # enabled

  origin {
    domain_name = "example.data.mediastore.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "match-viewer"  # Does not enforce HTTPS only, matches RQL condition to fail
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}


# fail: enabled=true; origin->custom_origin_config->origin_protocol_policy=match-viewer; origin->domain_name contains "mediastore" (second only)
resource "aws_cloudfront_distribution" "example_fail_one_good_one_bad" {
  enabled = true # enabled

  origin {
    domain_name = "example.com" # safe domain
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "https-only"  # HTTPS only
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  origin {
    domain_name = "example.data.mediastore.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "match-viewer"  # Does not enforce HTTPS only, matches RQL condition to fail
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# fail: enabled=true; origin->custom_origin_config->origin_protocol_policy=match-viewer; origin->domain_name contains "elb" (second only) and first doesn't have custom_origin_config
resource "aws_cloudfront_distribution" "example_fail_one_missing_one_bad" {
  enabled = true # enabled

  origin {
    domain_name = "example.com" # safe domain
    origin_id   = "custom-origin-example"

    # no custom_origin_config
  }

  origin {
    domain_name = "example.elb.amazonaws.com" # contains dangerous domain name
    origin_id   = "custom-origin-example"

    custom_origin_config {
      origin_protocol_policy = "match-viewer"  # Does not enforce HTTPS only, matches RQL condition to fail
      http_port              = 80
      https_port             = 443
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "custom-origin-example"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl = 0
    default_ttl = 3600
    max_ttl = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
