variable "vpc_id" {
  type = string
}

variable "cidr_sg" {
  type    = string
  default = "0.0.0.0/0"
}

resource "aws_security_group" "sg" {
  name            = "example"
  vpc_id          = var.vpc_id

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "TCP"
    cidr_blocks     = [var.cidr_sg]
  }
  egress {
    from_port       = 22
    to_port         = 22
    protocol        = "TCP"
    cidr_blocks     = ["10.0.0.0/16", var.cidr_sg]
  }
}
