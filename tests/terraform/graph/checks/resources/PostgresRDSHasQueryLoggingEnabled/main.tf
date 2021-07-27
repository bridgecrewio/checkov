resource "aws_db_instance" "pass" {
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  name                 = "mydb"
  parameter_group_name = "aws_rds_cluster_parameter_group.pass.name"
}

//no parameter_group_name set
resource "aws_db_instance" "fail" {
  engine         = "postgres"
  instance_class = "db.t3.micro"
  name           = "mydb"
}

// no postgres
resource "aws_db_instance" "ignore" {
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
  name        = "rds-cluster-pg-fail"
  family      = "postgres11"
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
//resource "aws_rds_cluster_parameter_group" "pass" {
//  name        = "rds-cluster-pg-pass"
//  family      = "aurora-postgresql11"
//  description = "RDS default cluster parameter group"

//  parameter {
//    name  = "character_set_server"
//    value = "utf8"
//  }

//  parameter {
//    name  = "character_set_client"
//    value = "utf8"
//  }
}