resource "aws_db_instance" "pass" {
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  parameter_group_name = aws_rds_cluster_parameter_group.pass.id
}

resource "aws_db_instance" "fail3" {
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  parameter_group_name = aws_rds_cluster_parameter_group.fail.id
}

resource "aws_db_instance" "fail4" {
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  parameter_group_name = aws_rds_cluster_parameter_group.fail2.id
}

//no parameter_group_name set
resource "aws_db_instance" "fail" {
  engine         = "postgres"
  instance_class = "db.t3.micro"
  name           = "mydb"
}

//not postgres
resource "aws_db_instance" "ignore" {
  engine         = "mysql"
  instance_class = "db.t3.micro"
  name           = "mydb"
}

// no postgres
resource "aws_db_instance" "ignore2" {
  allocated_storage    = 10
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  username             = "foo"
  password             = "foobarbaz"
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}

//not correct params
resource "aws_rds_cluster_parameter_group" "fail" {
  name        = "mysql-cluster-fail"
  family      = "mysql"
  description = "RDS default cluster parameter group"

  parameter {
    name  = "character_set_server"
    value = "utf8"
  }

  parameter {
    name  = "character_set_client"
    value = "utf8"
  }
}

provider "aws" {
  region="eu-west-2"
}

//will be correct params
resource "aws_rds_cluster_parameter_group" "pass" {
  name        = "rds-cluster-pg-pass"
  family      = "aurora-postgresql11"
  description = "RDS default cluster parameter group"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "250ms"
  }
}

resource "aws_rds_cluster_parameter_group" "fail2" {
  name        = "rds-cluster-pg-pass"
  family      = "aurora-postgresql11"
  description = "RDS default cluster parameter group"

  parameter {
    name  = "log_statement"
    value = "all"
  }
}

resource "aws_db_instance" "ignore3" {
  identifier                    = "xxx-our-unique-id"
  allocated_storage             = 1000
  storage_type                  = "gp2"
  copy_tags_to_snapshot         = true
  engine                        = "sqlserver-se"
  engine_version                = "15.00.4043.16.v1"
  license_model                 = "license-included"
  instance_class                = "db.r5.4xlarge"
  name                          = ""
  username                      = "sa"
  password                      = var.password
  port                          = 1433
  publicly_accessible           = false
  security_group_names          = []
  vpc_security_group_ids        = ["sg-xxxxx"]
  db_subnet_group_name          = "dbsubnet"
  performance_insights_enabled  = true
  option_group_name             = "sql-std-2019"
  deletion_protection           = true
  max_allocated_storage         = 1500
  parameter_group_name          = "sql-server-2019-std"
  character_set_name            = "SQL_Latin1_General_CP1_CS_AS"
  # checkov:skip=CKV_AWS_157:Web db, acceptable risk until Resize
  multi_az                      = false
  backup_retention_period       = 35
  enabled_cloudwatch_logs_exports = ["agent","error"]
  backup_window                 = "11:17-11:47"
  maintenance_window            = "sat:07:13-sat:08:43"
  final_snapshot_identifier     = "xxx-unique-name-final"
}
