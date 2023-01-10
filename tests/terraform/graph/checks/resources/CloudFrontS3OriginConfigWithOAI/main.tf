
resource "aws_s3_bucket" "bucket" {
  bucket = "mybucket"

  tags = {
    Name = "My bucket"
  }
}

// S3 origin with OAI in `s3_origin_config`
resource "aws_cloudfront_distribution" "pass_1" {
  origin {
    domain_name = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_id   = "failoverS3"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.default.cloudfront_access_identity_path
    }
  }
}

// S3 origin with OAI via `origin_access_control_id`
resource "aws_cloudfront_distribution" "pass_2" {
  origin {
    domain_name = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_id   = "failoverS3"
    origin_access_control_id = aws_cloudfront_origin_access_control.default.id
  }
}

// Custom origin (not connected to bucket)
resource "aws_cloudfront_distribution" "pass_3" {
  origin {
    domain_name = "https://example.com"
    origin_id   = "custom"
  }
}

// S3 origin without `s3_origin_config` nor `origin_access_control_id`
resource "aws_cloudfront_distribution" "fail_1" {
  origin {
    domain_name = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_id   = "failoverS3"
  }
}

// S3 origin with `s3_origin_config` but no `origin_access_control`
resource "aws_cloudfront_distribution" "fail_2" {
  origin {
    domain_name = aws_s3_bucket.bucket.bucket_regional_domain_name
    origin_id   = "failoverS3"
    s3_origin_config {
      // Nothing
    }
  }
}