resource "aws_cloudfront_distribution" "pass_1" {

  origin {
    domain_name = aws_s3_bucket.primary.bucket_regional_domain_name
    origin_id   = "primaryS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
   target_origin_id = "groupS3"
  }

  viewer_certificate {
    acm_certificate_arn = "aaaaa"
  }
}

resource "aws_cloudfront_distribution" "pass_2" {

  origin {
    domain_name = aws_s3_bucket.primary.bucket_regional_domain_name
    origin_id   = "primaryS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
   target_origin_id = "groupS3"
  }

  viewer_certificate {
    acm_certificate_arn = "aaaaa"
    iam_certificate_id = "adaffwqfwff"
  }
}

resource "aws_cloudfront_distribution" "fail" {

  origin {
    domain_name = aws_s3_bucket.primary.bucket_regional_domain_name
    origin_id   = "primaryS3"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    target_origin_id = "groupS3"
  }

  viewer_certificate {
    cloudfront_default_certificate = "test"
  }
}