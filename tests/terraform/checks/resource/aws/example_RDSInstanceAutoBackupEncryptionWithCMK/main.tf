resource "aws_db_instance_automated_backups_replication" "fail" {
  source_db_instance_arn = "arn:aws:rds:us-west-2:123456789012:db:mydatabase"
  retention_period       = 14
}

resource "aws_db_instance_automated_backups_replication" "pass" {
  source_db_instance_arn = "arn:aws:rds:us-west-2:123456789012:db:mydatabase"
  kms_key_id             = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
}