resource "aws_rds_cluster" "pass" {
  backup_retention_period = 35
}

resource "aws_rds_cluster" "pass2" {
}

resource "aws_rds_cluster" "fail2" {
  backup_retention_period = 0
}

#this will fail in tf i dont know why we even bother?
resource "aws_rds_cluster" "fail" {
  backup_retention_period = 36
}

resource "aws_db_instance" "pass" {
  backup_retention_period = 35
}

resource "aws_db_instance" "pass2" {
}

resource "aws_db_instance" "fail2" {
  backup_retention_period = 0
}

#this will fail in tf i dont know why we even bother?
resource "aws_db_instance" "fail" {
  backup_retention_period = 36
}

resource "aws_db_instance" "unknown" {
  backup_retention_period = var.backup_retention_period
}
