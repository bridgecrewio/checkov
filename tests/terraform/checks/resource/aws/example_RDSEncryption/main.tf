# pass

resource "aws_db_instance" "enabled" {
  name           = "name"
  engine         = "mysql"
  instance_class = "db.t3.micro"

  storage_encrypted = true
}

# fail

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
