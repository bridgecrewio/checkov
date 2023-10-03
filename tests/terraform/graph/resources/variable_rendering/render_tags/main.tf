locals {
  api_tags      = merge({Key1: "Value1"}, local.tags)

    tags = {
    org          = "try-bridgecrew"
  }
}


resource "aws_cloudfront_distribution" "cloudfront" {
  tags            = local.api_tags
  enabled         = false
  default_cache_behavior {
    allowed_methods        = []
    cached_methods         = []
    target_origin_id       = ""
    viewer_protocol_policy = ""
  }
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