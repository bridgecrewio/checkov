resource "aws_cloudtrail" "fail" {
  name                          = "TRAIL"
  s3_bucket_name                = aws_s3_bucket.test.id
  include_global_service_events = true
}

resource "aws_cloudtrail" "pass" {
  name                          = "TRAIL"
  s3_bucket_name                = aws_s3_bucket.test.id
  include_global_service_events = true
  kms_key_id                    = aws_kms_key.test.arn
}