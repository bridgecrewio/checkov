resource "awscc_sns_topic" "pass" {
  topic_name = "pass"
  kms_master_key_id = awscc_kms_key.example.arn
}

resource "awscc_sns_topic" "fail" {
  topic_name = "fail"
}
