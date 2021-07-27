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
  engine         = "mysql"
  instance_class = "db.t3.micro"
  name           = "mydb"
}

// no postgres
resource "aws_db_instance" "fail2" {
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