variable "key" {
  type    = string
  default = null
}

variable "other_key" {
  type    = string
  default = "key"
}

resource "aws_cloudwatch_log_group" "pass" {
  retention_in_days = 1
  kms_key_id        = var.key
}

resource "aws_cloudwatch_log_group" "with_key" {
  retention_in_days = 1
  kms_key_id        = var.other_key
}
