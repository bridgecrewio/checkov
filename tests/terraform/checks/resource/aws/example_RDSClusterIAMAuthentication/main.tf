# pass

resource "aws_rds_cluster" "enabled" {
  master_username = "username"
  master_password = "password"

  iam_database_authentication_enabled = true
}

# failure

resource "aws_rds_cluster" "default" {
  master_username = "username"
  master_password = "password"
}

resource "aws_rds_cluster" "disabled" {
  master_username = "username"
  master_password = "password"

  iam_database_authentication_enabled = false
}
