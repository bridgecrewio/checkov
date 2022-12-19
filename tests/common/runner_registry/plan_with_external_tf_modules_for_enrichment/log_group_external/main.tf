resource "aws_cloudwatch_log_group" "this" {
  # checkov:skip=CKV_AWS_158: skip it

  count = var.create ? 1 : 0

  name              = var.name
  name_prefix       = var.name_prefix
  retention_in_days = var.retention_in_days
  kms_key_id        = var.kms_key_id

  tags = var.tags
}
