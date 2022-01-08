resource "aws_db_instance" "aws_db_instance_ok" {
  allocated_storage       = 10
  engine                  = "mysql"
  engine_version          = "5.7"
  instance_class          = "db.t3.micro"
  name                    = "mydb"
  username                = "foo"
  password                = "foobarbaz"
  parameter_group_name    = "default.mysql5.7"
  skip_final_snapshot     = true
  backup_retention_period = 8
}

#Default BackUp Retention is 7 Days
resource "aws_db_instance" "aws_db_instance_default_ok" {
  allocated_storage       = 10
  engine                  = "mysql"
  engine_version          = "5.7"
  instance_class          = "db.t3.micro"
  name                    = "mydb"
  username                = "foo"
  password                = "foobarbaz"
  parameter_group_name    = "default.mysql5.7"
  skip_final_snapshot     = true
}

resource "aws_db_instance" "aws_db_instance_not_ok" {
  allocated_storage       = 10
  engine                  = "mysql"
  engine_version          = "5.7"
  instance_class          = "db.t3.micro"
  name                    = "mydb"
  username                = "foo"
  password                = "foobarbaz"
  parameter_group_name    = "default.mysql5.7"
  skip_final_snapshot     = true
  backup_retention_period = 1
}