resource "aws_cloudfront_distribution" "pass" {
  dynamic "origin" {
    for_each = local.origins
    content {
      domain_name = origin.value["domain_name"]
      origin_id   = origin.value["origin_id"]

      s3_origin_config {
        origin_access_identity = origin.value["origin_access_identity"]
      }
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = var.default_behaviour.allowed_methods
    cached_methods   = var.default_behaviour.cached_methods
    target_origin_id = var.default_behaviour.origin_id

    forwarded_values {
      query_string = var.default_behaviour.query_string

      cookies {
        forward = var.default_behaviour.forward
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = var.default_behaviour.min_ttl
    default_ttl            = var.default_behaviour.default_ttl
    max_ttl                = var.default_behaviour.max_ttl
  }

  dynamic "ordered_cache_behavior" {
    for_each = var.behaviours
    content {
      path_pattern     = ordered_cache_behavior.value["path_pattern"]
      allowed_methods  = ordered_cache_behavior.value["allowed_methods"]
      cached_methods   = ordered_cache_behavior.value["cached_methods"]
      target_origin_id = ordered_cache_behavior.value["origin_id"]
      forwarded_values {
        headers      = ordered_cache_behavior.value["headers"]
        query_string = ordered_cache_behavior.value["query_string"]
        cookies {
          forward = ordered_cache_behavior.value["forward"]
        }
      }
      min_ttl                = ordered_cache_behavior.value["min_ttl"]
      default_ttl            = ordered_cache_behavior.value["default_ttl"]
      max_ttl                = ordered_cache_behavior.value["max_ttl"]
      compress               = ordered_cache_behavior.value["compress"]
      viewer_protocol_policy = "allow-all"
    }
  }

  price_class = "PriceClass_200"

  restrictions {
    geo_restriction {
      restriction_type = var.geo_restrictions["restriction_type"]
      locations        = var.geo_restrictions["locations"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.viewer_certificate["cloudfront_default_certificate"]
    minimum_protocol_version       = var.viewer_certificate["minimum_protocol_version"]
  }

  lifecycle {
    ignore_changes = [tags]
  }
  tags = {
    "key" = "value"
  }
}

resource "aws_cloudfront_distribution" "fail" {
  dynamic "origin" {
    for_each = local.origins
    content {
      domain_name = origin.value["domain_name"]
      origin_id   = origin.value["origin_id"]

      s3_origin_config {
        origin_access_identity = origin.value["origin_access_identity"]
      }
    }
  }

  enabled             = false
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = var.default_behaviour.allowed_methods
    cached_methods   = var.default_behaviour.cached_methods
    target_origin_id = var.default_behaviour.origin_id

    forwarded_values {
      query_string = var.default_behaviour.query_string

      cookies {
        forward = var.default_behaviour.forward
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = var.default_behaviour.min_ttl
    default_ttl            = var.default_behaviour.default_ttl
    max_ttl                = var.default_behaviour.max_ttl
  }

  dynamic "ordered_cache_behavior" {
    for_each = var.behaviours
    content {
      path_pattern     = ordered_cache_behavior.value["path_pattern"]
      allowed_methods  = ordered_cache_behavior.value["allowed_methods"]
      cached_methods   = ordered_cache_behavior.value["cached_methods"]
      target_origin_id = ordered_cache_behavior.value["origin_id"]
      forwarded_values {
        headers      = ordered_cache_behavior.value["headers"]
        query_string = ordered_cache_behavior.value["query_string"]
        cookies {
          forward = ordered_cache_behavior.value["forward"]
        }
      }
      min_ttl                = ordered_cache_behavior.value["min_ttl"]
      default_ttl            = ordered_cache_behavior.value["default_ttl"]
      max_ttl                = ordered_cache_behavior.value["max_ttl"]
      compress               = ordered_cache_behavior.value["compress"]
      viewer_protocol_policy = "allow-all"
    }
  }

  price_class = "PriceClass_200"

  restrictions {
    geo_restriction {
      restriction_type = var.geo_restrictions["restriction_type"]
      locations        = var.geo_restrictions["locations"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.viewer_certificate["cloudfront_default_certificate"]
    minimum_protocol_version       = var.viewer_certificate["minimum_protocol_version"]
  }

  lifecycle {
    ignore_changes = [tags]
  }
  tags = {
    "key" = "value"
  }
}
