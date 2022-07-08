resource "aws_cloudtrail" "fail" {
  name                          = "TRAIL"
  s3_bucket_name                = aws_s3_bucket.test.id
  include_global_service_events = true
  enable_logging                = false
  is_multi_region_trail         = false
  tags                          = { test = "Fail" }
}

resource "aws_cloudtrail" "pass" {
  name                          = "TRAIL"
  s3_bucket_name                = aws_s3_bucket.test.id
  include_global_service_events = true
  enable_logging                = false
  is_multi_region_trail         = false
  sns_topic_name                = aws_sns_topic.notes.arn
  tags                          = { test = "Fail" }
}

resource "aws_sns_topic" "notes" {}