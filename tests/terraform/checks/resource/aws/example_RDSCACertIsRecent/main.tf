
resource "aws_db_instance" "fail" {
  allocated_storage                   = 20
  storage_type                        = "gp2"
  engine                              = "mysql"
  engine_version                      = "5.7"
  instance_class                      = "db.t2.micro"
  db_name                             = "mydb"
  username                            = "foo"
  password                            = "foobarbaz"
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
  ca_cert_identifier                  = "rds-ca-2015"
}

locals {
  passing_ca_cert_identifiers = [
    "rds-ca-rsa2048-g1",
    "rds-ca-rsa4096-g1",
    "rds-ca-ecc384-g1",
  ]
}

resource "aws_db_instance" "pass" {
  for_each                            = local.passing_ca_cert_identifiers
  allocated_storage                   = 20
  storage_type                        = "gp2"
  engine                              = "mysql"
  engine_version                      = "5.7"
  instance_class                      = "db.t2.micro"
  db_name                             = "mydb"
  username                            = "foo"
  password                            = "foobarbaz"
  iam_database_authentication_enabled = true
  storage_encrypted                   = true
  ca_cert_identifier                  = each.key
}
