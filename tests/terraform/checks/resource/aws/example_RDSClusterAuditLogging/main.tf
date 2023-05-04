# pass

resource "aws_rds_cluster" "pass" {
  master_username = "username"
  master_password = "password"
  enabled_cloudwatch_logs_exports = ["audit"]
  iam_database_authentication_enabled = true
}

resource "aws_rds_cluster" "pass2" {
  master_username = "username"
  master_password = "password"
  enabled_cloudwatch_logs_exports = ["general", "audit"]
  iam_database_authentication_enabled = true
  engine = "aurora-mysql"
}

resource "aws_rds_cluster" "fail" {
  master_username = "username"
  master_password = "password"
}

resource "aws_rds_cluster" "fail2" {
  master_username = "username"
  master_password = "password"
  enabled_cloudwatch_logs_exports = ["error", "general", "slowquery"]
  iam_database_authentication_enabled = false
}

# unknown

resource "aws_rds_cluster" "unknown" {
  master_username = "username"
  master_password = "password"

  engine = "aurora-postgresql"
}
