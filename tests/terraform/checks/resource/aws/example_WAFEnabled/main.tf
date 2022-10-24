# pass

resource "aws_cloudfront_distribution" "pass" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "var.price_class"
  tags                = "var.common_tags"

  web_acl_id = "IsSetToAValue"

  origin {
    domain_name = "aws_s3_bucket.website.bucket_regional_domain_name"
    origin_id   = "origin"
    s3_origin_config {
      origin_access_identity = "aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path"
    }
  }
  default_cache_behavior {
    allowed_methods        = []
    cached_methods         = []
    target_origin_id       = ""
    viewer_protocol_policy = ""
  }
  restrictions {
    geo_restriction {
      restriction_type = ""
    }
  }
  viewer_certificate {}
}

# fail

resource "aws_cloudfront_distribution" "fail" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "var.price_class"
  tags                = "var.common_tags"

  origin {
    domain_name = "aws_s3_bucket.website.bucket_regional_domain_name"
    origin_id   = "origin"
    s3_origin_config {
      origin_access_identity = "aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path"
    }
  }
  default_cache_behavior {
    allowed_methods        = []
    cached_methods         = []
    target_origin_id       = ""
    viewer_protocol_policy = ""
  }
  restrictions {
    geo_restriction {
      restriction_type = ""
    }
  }
  viewer_certificate {}
}
