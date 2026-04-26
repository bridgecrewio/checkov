resource "aws_cloudfront_distribution" "pass_v1" {
  comment = "legacy logging"

  logging_config {
    bucket = "logs.s3.amazonaws.com"
  }

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

  enabled             = true
  default_root_object = "index.html"

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

resource "aws_cloudfront_distribution" "pass_v2" {
  comment = "v2 logging via cloudwatch log delivery"

  origin {
    domain_name = "example.org"
    origin_id   = "example-origin-2"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    target_origin_id       = "example-origin-2"
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

resource "aws_cloudwatch_log_delivery_source" "pass_v2" {
  name         = "cf-source-pass-v2"
  log_type     = "ACCESS_LOGS"
  resource_arn = aws_cloudfront_distribution.pass_v2.arn
}

resource "aws_cloudwatch_log_delivery_destination" "pass_v2" {
  name = "cf-dest-pass-v2"

  delivery_destination_configuration {
    destination_resource_arn = "arn:aws:logs:us-east-1:111111111111:log-group:/aws/cloudfront/pass-v2:*"
  }
}

resource "aws_cloudwatch_log_delivery" "pass_v2" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.pass_v2.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.pass_v2.arn
}

resource "aws_cloudfront_distribution" "fail_no_logging" {
  comment = "no logging at all"

  origin {
    domain_name = "example.net"
    origin_id   = "example-origin-3"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    target_origin_id       = "example-origin-3"
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

resource "aws_cloudfront_distribution" "fail_v2_incomplete_chain" {
  comment = "source exists, delivery missing"

  origin {
    domain_name = "example.edu"
    origin_id   = "example-origin-4"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    target_origin_id       = "example-origin-4"
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
  name         = "cf-source-fail-v2"
  log_type     = "ACCESS_LOGS"
  resource_arn = aws_cloudfront_distribution.fail_v2_incomplete_chain.arn
}
