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

variable "empty_ingress" {
  type = list
}

resource "aws_security_group" "multiple_ingress_sg" {
  name            = "example"
  vpc_id          = var.vpc_id

  ingress = [var.empty_ingress]
  ingress = [
    {
    from_port       = 23
    to_port         = 23
    protocol        = "TCP"
    cidr_blocks     = [var.cidr_sg]
  },
    var.empty_ingress
  ]

  egress {
    from_port       = 22
    to_port         = 22
    protocol        = "TCP"
    cidr_blocks     = ["10.0.0.0/16", var.cidr_sg]
  }
}
