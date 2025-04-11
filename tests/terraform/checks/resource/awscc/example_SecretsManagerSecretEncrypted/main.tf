resource "awscc_secretsmanager_secret" "pass" {
  name = "my-encrypted-secret"
  description = "Secret encrypted with CMK"
  kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/1234abcd-12ab-34cd-56ef-1234567890ab"
}

resource "awscc_secretsmanager_secret" "fail" {
  name = "my-default-secret"
  description = "Secret using default encryption"
  # No KMS key specified - uses AWS owned key
}
