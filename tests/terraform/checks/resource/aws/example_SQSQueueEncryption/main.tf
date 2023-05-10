//sqs_managed_sse_enabled defaults to false
resource "aws_sqs_queue" "fail" {
  name = "terraform-example-queue"
}

resource "aws_sqs_queue" "pass" {
  name                              = "terraform-example-queue"
  kms_master_key_id                 = "alias/aws/sqs"
  kms_data_key_reuse_period_seconds = 300
}

resource "aws_sqs_queue" "fail2" {
  name                              = "terraform-example-queue"
  kms_master_key_id                 = ""
  kms_data_key_reuse_period_seconds = 300
}

resource "aws_sqs_queue" "fail3" {
  name                    = "unencrypted-queue"
  sqs_managed_sse_enabled = false
}

resource "aws_sqs_queue" "pass2" {
  name                    = "unencrypted-queue"
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "pass3" {
  name                              = "unencrypted-queue"
  kms_master_key_id                 = "alias/aws/sqs"
  kms_data_key_reuse_period_seconds = 300
  sqs_managed_sse_enabled           = false
}
