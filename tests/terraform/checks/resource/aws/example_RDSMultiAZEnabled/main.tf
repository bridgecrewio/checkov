# fail
resource "aws_db_instance" "disabled" {
  name   = "name"
  engine = "mysql"

  identifier     = "id"
  instance_class = "foo"
  multi_az       = false
}

# fail
resource "aws_db_instance" "default" {
  name   = "name"
  engine = "mysql"

  identifier     = "id"
  instance_class = "foo"
}

# pass
resource "aws_db_instance" "enabled" {
  name   = "name"
  engine = "mysql"

  identifier     = "id"
  instance_class = "foo"
  multi_az       = true
}