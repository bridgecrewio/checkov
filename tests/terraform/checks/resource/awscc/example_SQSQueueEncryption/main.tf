resource "awscc_sqs_queue" "pass_kms" {
  queue_name       = "encrypted-queue-kms"
  kms_master_key_id = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
}

resource "awscc_sqs_queue" "pass_sqs_managed" {
  queue_name            = "encrypted-queue-sqs-managed"
  sqs_managed_sse_enabled = true
}

resource "awscc_sqs_queue" "fail" {
  queue_name = "unencrypted-queue"
  # No encryption specified
}
