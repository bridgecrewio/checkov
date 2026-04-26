# pass: distribution with legacy v1 logging_config

resource "aws_cloudfront_distribution" "pass_v1" {
  enabled = true

  logging_config {
    bucket = "logs.s3.amazonaws.com"
  }

  origin {
    domain_name = "example-v1.com"
    origin_id   = "example-origin-v1"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "example-origin-v1"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
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

# pass: distribution with complete v2 CloudWatch log delivery chain

resource "aws_cloudfront_distribution" "pass" {
  enabled = true

  origin {
    domain_name = "example.com"
    origin_id   = "example-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "example-origin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
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

resource "aws_cloudwatch_log_delivery_source" "pass" {
  name         = "cf-source-pass"
  log_type     = "ACCESS_LOGS"
  resource_arn = aws_cloudfront_distribution.pass.arn
}

resource "aws_cloudwatch_log_delivery_destination" "pass" {
  name = "cf-dest-pass"

  delivery_destination_configuration {
    destination_resource_arn = "arn:aws:logs:us-east-1:111111111111:log-group:/aws/cloudfront/pass:*"
  }
}

resource "aws_cloudwatch_log_delivery" "pass" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.pass.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.pass.arn
}

# fail: distribution with no log delivery source attached

resource "aws_cloudfront_distribution" "fail" {
  enabled = true

  origin {
    domain_name = "example.net"
    origin_id   = "example-origin-fail"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "example-origin-fail"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
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

# fail: distribution with source attached but incomplete v2 chain (no delivery)

resource "aws_cloudfront_distribution" "fail_v2_incomplete_chain" {
  enabled = true

  origin {
    domain_name = "example-incomplete.net"
    origin_id   = "example-origin-incomplete"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "example-origin-incomplete"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
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

resource "aws_cloudwatch_log_delivery_source" "fail_v2_incomplete_chain" {
  name         = "cf-source-fail-incomplete"
  log_type     = "ACCESS_LOGS"
  resource_arn = aws_cloudfront_distribution.fail_v2_incomplete_chain.arn
}
