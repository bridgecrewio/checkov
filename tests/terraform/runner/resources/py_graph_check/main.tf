provider "aws" {
  use_fips_endpoint = true
}

resource "aws_db_instance" "storage_encrypted_enabled" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  storage_encrypted = true
}

resource "aws_db_instance" "default_connected_to_provider_with_fips" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  provider = "aws"
}

# Fail

resource "aws_db_instance" "default" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"
}

resource "aws_db_instance" "disabled" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  storage_encrypted = False
}
