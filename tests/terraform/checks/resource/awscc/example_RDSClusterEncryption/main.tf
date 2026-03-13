resource "awscc_rds_db_cluster" "pass" {
  db_cluster_identifier = "encrypted-aurora-cluster"
  engine                = "aurora-mysql"
  engine_version        = "5.7.mysql_aurora.2.10.2"
  master_username       = "admin"
  master_user_password  = "Password123"
  storage_encrypted     = true
}

resource "awscc_rds_db_cluster" "fail" {
  db_cluster_identifier = "unencrypted-aurora-cluster"
  engine                = "aurora-mysql"
  engine_version        = "5.7.mysql_aurora.2.10.2"
  master_username       = "admin"
  master_user_password  = "Password123"
  storage_encrypted     = false
}

resource "awscc_rds_db_cluster" "fail2" {
  db_cluster_identifier = "default-aurora-cluster"
  engine                = "aurora-mysql"
  engine_version        = "5.7.mysql_aurora.2.10.2"
  master_username       = "admin"
  master_user_password  = "Password123"
  # storage_encrypted defaults to false
}
