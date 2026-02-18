resource "awscc_cloudtrail_trail" "pass" {
  trail_name                 = "pass"
  is_logging                 = true
  s3_bucket_name             = awscc_s3_bucket.example.id
  enable_log_file_validation = true

}

resource "awscc_cloudtrail_trail" "fail" {
  trail_name                 = "fail"
  is_logging                 = true
  s3_bucket_name             = awscc_s3_bucket.example.id
  enable_log_file_validation = false
}

resource "awscc_cloudtrail_trail" "fail2" {
  trail_name     = "fail2"
  is_logging     = true
  s3_bucket_name = awscc_s3_bucket.example.id
}
