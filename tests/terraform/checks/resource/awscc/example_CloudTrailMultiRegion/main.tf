resource "awscc_cloudtrail_trail" "pass" {
  name                          = "multi-region-trail"
  s3_bucket_name                = "aws-cloudtrail-logs-123456789012-abcdefg"
  is_multi_region_trail         = true
  include_global_service_events = true
}

resource "awscc_cloudtrail_trail" "fail" {
  name                          = "single-region-trail"
  s3_bucket_name                = "aws-cloudtrail-logs-123456789012-abcdefg"
  is_multi_region_trail         = false
  include_global_service_events = true
}

resource "awscc_cloudtrail_trail" "fail2" {
  name                          = "default-region-trail"
  s3_bucket_name                = "aws-cloudtrail-logs-123456789012-abcdefg"
  # is_multi_region_trail defaults to false
  include_global_service_events = true
}
