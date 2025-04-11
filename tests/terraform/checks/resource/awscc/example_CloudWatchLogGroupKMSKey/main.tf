resource "awscc_logs_log_group" "pass" {
  log_group_name = "example-encrypted-log-group"
  kms_key_id     = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
}

resource "awscc_logs_log_group" "fail" {
  log_group_name = "example-unencrypted-log-group"
  # No KMS key specified
}
