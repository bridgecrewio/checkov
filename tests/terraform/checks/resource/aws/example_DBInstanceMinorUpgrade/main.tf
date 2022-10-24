resource "aws_rds_cluster_instance" "fail" {
  name                         = "bar"
  performance_insights_enabled = false
  publicly_accessible          = true
  auto_minor_version_upgrade   = false
  tags                         = { test = "Fail" }
}

resource "aws_rds_cluster_instance" "fail2" {
  name                         = "bar"
  performance_insights_enabled = false
  publicly_accessible          = true
  tags                         = { test = "Fail" }
}

resource "aws_rds_cluster_instance" "pass" {
  name                         = "bar"
  performance_insights_enabled = false

  # performance_insights_kms_key_id = ""
  # kms_key_id                      = ""
  publicly_accessible        = true
  auto_minor_version_upgrade = true
  tags                       = { test = "Fail" }
}

resource "aws_db_instance" "pass" {
  //storage_encrypted  = true
  publicly_accessible        = true
  backup_retention_period    = 0
  engine                     = "postgres"
  auto_minor_version_upgrade = true
  tags                       = { test = "Fail" }
}

resource "aws_db_instance" "fail" {
  //storage_encrypted  = true
  publicly_accessible        = true
  backup_retention_period    = 0
  engine                     = "postgres"
  auto_minor_version_upgrade = false
  tags                       = { test = "Fail" }
}

resource "aws_db_instance" "fail2" {
  //storage_encrypted  = true
  publicly_accessible     = true
  backup_retention_period = 0
  engine                  = "postgres"
  tags                    = { test = "Fail" }
}