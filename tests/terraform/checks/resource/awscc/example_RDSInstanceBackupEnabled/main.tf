resource "awscc_rds_db_instance" "pass" {
  allocated_storage     = 20
  db_instance_class     = "db.t3.micro"
  engine               = "mysql"
  engine_version       = "8.0"
  db_instance_identifier = "mydb-with-backup"
  username             = "admin"
  password             = "password123"
  backup_retention_period = 7
}

resource "awscc_rds_db_instance" "fail" {
  allocated_storage     = 20
  db_instance_class     = "db.t3.micro"
  engine               = "mysql"
  engine_version       = "8.0"
  db_instance_identifier = "mydb-no-backup"
  username             = "admin"
  password             = "password123"
  backup_retention_period = 0
}

resource "awscc_rds_db_instance" "pass2" {
  allocated_storage     = 20
  db_instance_class     = "db.t3.micro"
  engine               = "mysql"
  engine_version       = "8.0"
  db_instance_identifier = "mydb-default-backup"
  username             = "admin"
  password             = "password123"
  # Default backup_retention_period is 1
}
