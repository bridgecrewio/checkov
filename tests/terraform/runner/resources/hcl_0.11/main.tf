resource "aws_db_instance" "test_db" {
  apply_immediately       = "true"
  allocated_storage       = 100
  skip_final_snapshot     = true
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "11.5"
  instance_class          = "db.t3.small"
  identifier              = "techops"
  name                    = "postgres"
  username                = "postgres"
  backup_retention_period = "1"
  maintenance_window      = "mon:01:00-mon:01:30"
  storage_encrypted       = "0"
  multi_az                = "false"
  tags = {
    workload-type = "other"
  }
}
