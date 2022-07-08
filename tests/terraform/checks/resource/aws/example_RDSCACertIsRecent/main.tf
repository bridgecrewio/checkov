
resource "aws_db_instance" "fail" {
  allocated_storage                   = 20
  storage_type                        = "gp2"
  engine                              = "mysql"
  engine_version                      = "5.7"
  instance_class                      = "db.t2.micro"
  name                                = "mydb"
  username                            = "foo"
  password                            = "foobarbaz"
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
  ca_cert_identifier                  = "rds-ca-2015"
}

resource "aws_db_instance" "pass" {
  allocated_storage                   = 20
  storage_type                        = "gp2"
  engine                              = "mysql"
  engine_version                      = "5.7"
  instance_class                      = "db.t2.micro"
  name                                = "mydb"
  username                            = "foo"
  password                            = "foobarbaz"
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
  ca_cert_identifier                  = "rds-ca-2019"
}

resource "aws_db_instance" "pass2" {
  allocated_storage                   = 20
  storage_type                        = "gp2"
  engine                              = "mysql"
  engine_version                      = "5.7"
  instance_class                      = "db.t2.micro"
  name                                = "mydb"
  username                            = "foo"
  password                            = "foobarbaz"
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
}
