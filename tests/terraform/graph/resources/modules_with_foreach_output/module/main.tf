resource "aws_security_group" "this" {
  name   = var.name
  vpc_id = "vpc-12345678"
}
