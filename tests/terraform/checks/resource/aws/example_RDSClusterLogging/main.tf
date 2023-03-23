
resource "aws_rds_cluster" "pass" {
  master_username = "username"
  master_password = "password"
  enabled_cloudwatch_logs_exports = ["audit"]
  iam_database_authentication_enabled = true
}

resource "aws_rds_cluster" "fail" {
  master_username = "username"
  master_password = "password"
}

