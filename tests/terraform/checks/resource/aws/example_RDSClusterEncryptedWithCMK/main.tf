# pass

resource "aws_rds_cluster" "pass" {
  master_username = "username"
  master_password = "password"
  storage_encrypted = true
  iam_database_authentication_enabled = true
  kms_key_id = aws_kms_key.pike.arn
}

# failure

resource "aws_rds_cluster" "fail" {
  master_username = "username"
  master_password = "password"
}

