resource "awscc_rds_db_instance" "pass" {
  db_instance_identifier = "my-protected-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  db_instance_class      = "db.t3.micro"
  allocated_storage      = 20
  deletion_protection    = true
}

resource "awscc_rds_db_instance" "fail" {
  db_instance_identifier = "my-unprotected-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  db_instance_class      = "db.t3.micro"
  allocated_storage      = 20
  deletion_protection    = false
}

resource "awscc_rds_db_instance" "fail2" {
  db_instance_identifier = "my-default-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  db_instance_class      = "db.t3.micro"
  allocated_storage      = 20
  # deletion_protection defaults to false
}
