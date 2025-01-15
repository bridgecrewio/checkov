resource "aws_sqs_queue" "fail" {
  name                        = "example-queue"
  kms_master_key_id            = "alias/aws/sqs"  # Violates the RQL by using the AWS-managed key instead of a customer-managed key.
  
  # Other SQS queue attributes
  delay_seconds                = 0
  max_message_size             = 262144
  message_retention_seconds    = 345600
  receive_wait_time_seconds    = 0
  visibility_timeout_seconds   = 30
}


resource "aws_sqs_queue" "pass_notexists" {
  name                        = "example-queue"
  
  # Other SQS queue attributes
  delay_seconds                = 0
  max_message_size             = 262144
  message_retention_seconds    = 345600
  receive_wait_time_seconds    = 0
  visibility_timeout_seconds   = 30
}

resource "aws_sqs_queue" "pass_different_start" {
  name                        = "example-queue"
  kms_master_key_id           = "foo"

  
  # Other SQS queue attributes
  delay_seconds                = 0
  max_message_size             = 262144
  message_retention_seconds    = 345600
  receive_wait_time_seconds    = 0
  visibility_timeout_seconds   = 30
}
