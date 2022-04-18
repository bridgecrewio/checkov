# pass

resource "aws_db_instance" "pass" {
  name           = "name"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = "13.3"
}

resource "aws_rds_cluster" "pass" {
  engine = "aurora-postgresql"
  engine_version = "11.9"
}

# fail

resource "aws_db_instance" "fail" {
  name           = "name"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = "13.2"
}

resource "aws_rds_cluster" "fail" {
  engine = "aurora-postgresql"
  engine_version = "11.8"
}

resource "aws_db_instance" "fail_old" {
  name           = "name"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = "9.6.21"
}

# unknown

resource "aws_rds_cluster" "mysql_v1" {
}

resource "aws_db_instance" "mysql" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"
}

resource "aws_db_instance" "postgres_unknown" {
  name           = "name"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = var.engine_version
}


resource "aws_db_instance" "unknown_two_parts" {
  name           = "name"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = "9.6"
}